"""
Модели системы потоков обучения
"""
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.common.models import BaseModel, ActiveModel, OrderedModel, StatusChoices
from apps.users.models import User
from .managers import FlowManager, UserFlowManager
from .snapshot_models import TaskSnapshot, QuizSnapshot, QuizQuestionSnapshot


class Flow(BaseModel, ActiveModel):
    """
    Поток обучения - набор этапов для изучения определенной темы
    Может содержать статьи, задания и квизы
    """
    title = models.CharField(
        'Название',
        max_length=255,
        help_text='Название потока обучения'
    )
    description = models.TextField(
        'Описание',
        help_text='Подробное описание потока обучения'
    )
    estimated_duration_hours = models.PositiveIntegerField(
        'Ожидаемая продолжительность (часы)',
        null=True,
        blank=True,
        help_text='Примерное время прохождения в часах'
    )
    
    # Настройки доступа
    is_mandatory = models.BooleanField(
        'Обязательный',
        default=False,
        help_text='Обязателен ли поток для всех новых сотрудников'
    )
    auto_assign_departments = models.JSONField(
        'Автоназначение отделам',
        default=list,
        blank=True,
        help_text='Список отделов для автоматического назначения потока'
    )
    
    objects = FlowManager()
    
    class Meta:
        db_table = 'flows'
        verbose_name = 'Поток обучения'
        verbose_name_plural = 'Потоки обучения'
        ordering = ['title']
    
    def __str__(self):
        return self.title
    
    @property
    def total_steps(self):
        """Общее количество этапов в потоке"""
        return self.flow_steps.count()
    
    @property
    def required_steps(self):
        """Количество обязательных этапов"""
        return self.flow_steps.filter(is_required=True).count()
    
    def get_next_step_order(self):
        """Возвращает следующий порядковый номер для нового этапа"""
        last_step = self.flow_steps.order_by('-order').first()
        return (last_step.order + 1) if last_step else 1


class FlowStep(BaseModel, OrderedModel, ActiveModel):
    """
    Этап потока обучения
    Может содержать статью, задание или квиз
    """
    class StepType(models.TextChoices):
        ARTICLE = 'article', 'Статья'
        TASK = 'task', 'Задание'
        QUIZ = 'quiz', 'Квиз'
        MIXED = 'mixed', 'Смешанный'
    
    flow = models.ForeignKey(
        Flow,
        on_delete=models.CASCADE,
        related_name='flow_steps',
        verbose_name='Поток'
    )
    title = models.CharField(
        'Название этапа',
        max_length=255,
        help_text='Название этапа потока'
    )
    description = models.TextField(
        'Описание',
        help_text='Описание того, что нужно сделать на этом этапе'
    )
    step_type = models.CharField(
        'Тип этапа',
        max_length=20,
        choices=StepType.choices,
        help_text='Тип контента в этапе'
    )
    
    # Связи с контентом
    article = models.ForeignKey(
        'guides.Article',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='flow_steps',
        verbose_name='Статья'
    )
    
    # Настройки этапа
    is_required = models.BooleanField(
        'Обязательный',
        default=True,
        help_text='Обязателен ли этап для завершения потока'
    )
    estimated_time_minutes = models.PositiveIntegerField(
        'Ожидаемое время (минуты)',
        null=True,
        blank=True,
        help_text='Примерное время выполнения этапа'
    )
    
    class Meta:
        db_table = 'flow_steps'
        verbose_name = 'Этап потока'
        verbose_name_plural = 'Этапы потоков'
        unique_together = [('flow', 'order')]
        ordering = ['flow', 'order']
    
    def __str__(self):
        return f"{self.flow.title} - {self.title}"
    
    def get_content_object(self):
        """Возвращает объект контента (статья, задание или квиз)"""
        if self.step_type == self.StepType.ARTICLE and self.article:
            return self.article
        elif self.step_type == self.StepType.TASK:
            return getattr(self, 'task', None)
        elif self.step_type == self.StepType.QUIZ:
            return getattr(self, 'quiz', None)
        return None


class Task(BaseModel):
    """
    Задание - этап потока где нужно найти кодовое слово
    """
    flow_step = models.OneToOneField(
        FlowStep,
        on_delete=models.CASCADE,
        related_name='task',
        verbose_name='Этап потока'
    )
    title = models.CharField(
        'Название задания',
        max_length=255,
        help_text='Название задания'
    )
    description = models.TextField(
        'Описание задания',
        help_text='Подробное описание того, что нужно сделать'
    )
    instruction = models.TextField(
        'Инструкция',
        help_text='Инструкция где искать кодовое слово'
    )
    code_word = models.CharField(
        'Кодовое слово',
        max_length=100,
        help_text='Правильное кодовое слово'
    )
    hint = models.TextField(
        'Подсказка',
        null=True,
        blank=True,
        help_text='Подсказка для выполнения задания'
    )
    
    class Meta:
        db_table = 'tasks'
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'
    
    def __str__(self):
        return self.title
    
    def check_answer(self, answer):
        """Проверяет правильность ответа"""
        return answer.lower().strip() == self.code_word.lower().strip()


class Quiz(BaseModel, ActiveModel):
    """
    Квиз - набор вопросов для проверки знаний
    """
    flow_step = models.OneToOneField(
        FlowStep,
        on_delete=models.CASCADE,
        related_name='quiz',
        verbose_name='Этап потока'
    )
    title = models.CharField(
        'Название квиза',
        max_length=255,
        help_text='Название квиза'
    )
    description = models.TextField(
        'Описание',
        null=True,
        blank=True,
        help_text='Описание квиза'
    )
    passing_score_percentage = models.PositiveIntegerField(
        'Проходной балл (%)',
        default=70,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text='Минимальный процент правильных ответов для прохождения'
    )
    shuffle_questions = models.BooleanField(
        'Перемешивать вопросы',
        default=False,
        help_text='Показывать вопросы в случайном порядке'
    )
    shuffle_answers = models.BooleanField(
        'Перемешивать ответы',
        default=False,
        help_text='Показывать варианты ответов в случайном порядке'
    )
    
    class Meta:
        db_table = 'quizzes'
        verbose_name = 'Квиз'
        verbose_name_plural = 'Квизы'
    
    def __str__(self):
        return self.title
    
    @property
    def total_questions(self):
        """Общее количество вопросов в квизе"""
        return self.questions.count()
    
    def calculate_score(self, correct_answers):
        """Вычисляет процент правильных ответов"""
        if self.total_questions == 0:
            return 0
        return (correct_answers / self.total_questions) * 100
    
    def is_passing_score(self, correct_answers):
        """Проверяет, достаточен ли балл для прохождения"""
        score = self.calculate_score(correct_answers)
        return score >= self.passing_score_percentage


class QuizQuestion(BaseModel, OrderedModel):
    """
    Вопрос квиза
    """
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Квиз'
    )
    question = models.TextField(
        'Текст вопроса',
        help_text='Формулировка вопроса'
    )
    explanation = models.TextField(
        'Объяснение',
        null=True,
        blank=True,
        help_text='Объяснение правильного ответа'
    )
    
    class Meta:
        db_table = 'quiz_questions'
        verbose_name = 'Вопрос квиза'
        verbose_name_plural = 'Вопросы квизов'
        unique_together = [('quiz', 'order')]
        ordering = ['quiz', 'order']
    
    def __str__(self):
        return f"{self.quiz.title} - Вопрос {self.order}"
    
    @property
    def correct_answer(self):
        """Возвращает правильный ответ"""
        return self.answers.filter(is_correct=True).first()


class QuizAnswer(BaseModel, OrderedModel):
    """
    Вариант ответа на вопрос квиза
    """
    question = models.ForeignKey(
        QuizQuestion,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Вопрос'
    )
    answer_text = models.CharField(
        'Текст ответа',
        max_length=500,
        help_text='Вариант ответа'
    )
    is_correct = models.BooleanField(
        'Правильный ответ',
        default=False,
        help_text='Является ли этот ответ правильным'
    )
    explanation = models.TextField(
        'Объяснение',
        help_text='Объяснение почему ответ правильный или неправильный'
    )
    
    class Meta:
        db_table = 'quiz_answers'
        verbose_name = 'Ответ на вопрос'
        verbose_name_plural = 'Ответы на вопросы'
        unique_together = [('question', 'order')]
        ordering = ['question', 'order']
    
    def __str__(self):
        return f"{self.question} - {self.answer_text[:50]}"


class UserFlow(BaseModel):
    """
    Экземпляр прохождения потока конкретным пользователем
    """
    class FlowStatus(models.TextChoices):
        NOT_STARTED = 'not_started', 'Не начат'
        IN_PROGRESS = 'in_progress', 'В процессе'
        PAUSED = 'paused', 'Приостановлен'
        COMPLETED = 'completed', 'Завершен'
        SUSPENDED = 'suspended', 'Заблокировано'
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_flows',
        verbose_name='Пользователь'
    )
    flow = models.ForeignKey(
        Flow,
        on_delete=models.CASCADE,
        related_name='user_flows',
        verbose_name='Поток'
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=FlowStatus.choices,
        default=FlowStatus.NOT_STARTED,
        help_text='Текущий статус прохождения потока'
    )
    current_step = models.ForeignKey(
        FlowStep,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_user_flows',
        verbose_name='Текущий этап'
    )
    
    # Управление потоком
    paused_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='paused_flows',
        verbose_name='Приостановил'
    )
    paused_at = models.DateTimeField(
        'Время приостановки',
        null=True,
        blank=True
    )
    pause_reason = models.TextField(
        'Причина приостановки',
        null=True,
        blank=True
    )
    
    # Временные рамки
    expected_completion_date = models.DateField(
        'Ожидаемая дата завершения',
        null=True,
        blank=True,
        help_text='Дедлайн для завершения потока'
    )
    started_at = models.DateTimeField(
        'Время начала',
        null=True,
        blank=True
    )
    completed_at = models.DateTimeField(
        'Время завершения',
        null=True,
        blank=True
    )
    
    objects = UserFlowManager()
    
    class Meta:
        db_table = 'user_flows'
        verbose_name = 'Прохождение потока'
        verbose_name_plural = 'Прохождения потоков'
        unique_together = [('user', 'flow')]
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['flow', 'status']),
            models.Index(fields=['expected_completion_date']),
        ]
    
    def __str__(self):
        return f"{self.user.name} - {self.flow.title}"
    
    @property
    def is_overdue(self):
        """Проверяет, просрочено ли прохождение потока"""
        if not self.expected_completion_date:
            return False
        return (
            self.status in [self.FlowStatus.NOT_STARTED, self.FlowStatus.IN_PROGRESS] and
            timezone.now().date() > self.expected_completion_date
        )
    
    @property
    def progress_percentage(self):
        """Вычисляет процент завершения потока"""
        total_steps = self.flow.total_steps
        if total_steps == 0:
            return 100
        
        completed_steps = self.step_progress.filter(
            status=UserStepProgress.StepStatus.COMPLETED
        ).count()
        
        return (completed_steps / total_steps) * 100
    
    def start(self):
        """Запускает прохождение потока"""
        if self.status == self.FlowStatus.NOT_STARTED:
            self.status = self.FlowStatus.IN_PROGRESS
            self.started_at = timezone.now()
            self.current_step = self.flow.flow_steps.filter(is_active=True).first()
            self.save()
    
    def pause(self, paused_by, reason=None):
        """Приостанавливает прохождение потока"""
        if self.status == self.FlowStatus.IN_PROGRESS:
            self.status = self.FlowStatus.PAUSED
            self.paused_by = paused_by
            self.paused_at = timezone.now()
            self.pause_reason = reason
            self.save()
    
    def resume(self):
        """Возобновляет прохождение потока"""
        if self.status == self.FlowStatus.PAUSED:
            self.status = self.FlowStatus.IN_PROGRESS
            self.paused_by = None
            self.paused_at = None
            self.pause_reason = None
            self.save()
    
    def complete(self):
        """Завершает прохождение потока"""
        if self.status in [self.FlowStatus.IN_PROGRESS, self.FlowStatus.PAUSED]:
            self.status = self.FlowStatus.COMPLETED
            self.completed_at = timezone.now()
            self.save()


class FlowBuddy(BaseModel):
    """
    Бадди для конкретного экземпляра прохождения потока
    Может управлять процессом обучения подопечного
    """
    user_flow = models.ForeignKey(
        UserFlow,
        on_delete=models.CASCADE,
        related_name='flow_buddies',
        verbose_name='Прохождение потока'
    )
    buddy_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='buddy_flows',
        verbose_name='Бадди'
    )
    
    # Права бадди
    can_pause_flow = models.BooleanField(
        'Может приостанавливать',
        default=True,
        help_text='Может ли бадди приостанавливать поток'
    )
    can_resume_flow = models.BooleanField(
        'Может возобновлять',
        default=True,
        help_text='Может ли бадди возобновлять поток'
    )
    can_extend_deadline = models.BooleanField(
        'Может продлевать дедлайны',
        default=True,
        help_text='Может ли бадди продлевать сроки выполнения'
    )
    
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_buddy_flows',
        verbose_name='Назначил'
    )
    assigned_at = models.DateTimeField(
        'Дата назначения',
        default=timezone.now
    )
    is_active = models.BooleanField(
        'Активен',
        default=True,
        help_text='Активен ли бадди для данного потока'
    )
    
    class Meta:
        db_table = 'flow_buddies'
        verbose_name = 'Бадди потока'
        verbose_name_plural = 'Бадди потоков'
        unique_together = [('user_flow', 'buddy_user')]
        indexes = [
            models.Index(fields=['buddy_user', 'is_active']),
            models.Index(fields=['user_flow', 'is_active']),
        ]
    
    def __str__(self):
        return f"Бадди {self.buddy_user.name} для {self.user_flow}"


class UserStepProgress(BaseModel):
    """
    Прогресс пользователя по конкретному этапу потока
    """
    class StepStatus(models.TextChoices):
        LOCKED = 'locked', 'Заблокирован'
        AVAILABLE = 'available', 'Доступен'
        IN_PROGRESS = 'in_progress', 'В процессе'
        COMPLETED = 'completed', 'Завершен'
    
    user_flow = models.ForeignKey(
        UserFlow,
        on_delete=models.CASCADE,
        related_name='step_progress',
        verbose_name='Прохождение потока'
    )
    flow_step = models.ForeignKey(
        FlowStep,
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name='Этап потока'
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=StepStatus.choices,
        default=StepStatus.LOCKED,
        help_text='Статус прохождения этапа'
    )
    
    # Временные метки прогресса
    article_read_at = models.DateTimeField(
        'Статья прочитана',
        null=True,
        blank=True
    )
    task_completed_at = models.DateTimeField(
        'Задание выполнено',
        null=True,
        blank=True
    )
    quiz_completed_at = models.DateTimeField(
        'Квиз завершен',
        null=True,
        blank=True
    )
    
    # Результаты квиза
    quiz_correct_answers = models.PositiveIntegerField(
        'Правильных ответов в квизе',
        null=True,
        blank=True
    )
    quiz_total_questions = models.PositiveIntegerField(
        'Всего вопросов в квизе',
        null=True,
        blank=True
    )
    
    started_at = models.DateTimeField(
        'Время начала',
        null=True,
        blank=True
    )
    completed_at = models.DateTimeField(
        'Время завершения',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'user_step_progress'
        verbose_name = 'Прогресс по этапу'
        verbose_name_plural = 'Прогресс по этапам'
        unique_together = [('user_flow', 'flow_step')]
        indexes = [
            models.Index(fields=['user_flow', 'status']),
            models.Index(fields=['flow_step', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user_flow.user.name} - {self.flow_step.title}"
    
    @property
    def is_accessible(self):
        """Проверяет, доступен ли этап для выполнения"""
        # Первый этап всегда доступен
        if self.flow_step.order == 1:
            return True
        
        # Проверяем, завершен ли предыдущий этап
        previous_step = self.flow_step.flow.flow_steps.filter(
            order=self.flow_step.order - 1
        ).first()
        
        if not previous_step:
            return True
        
        previous_progress = UserStepProgress.objects.filter(
            user_flow=self.user_flow,
            flow_step=previous_step
        ).first()
        
        return (
            previous_progress and 
            previous_progress.status == self.StepStatus.COMPLETED
        )
    
    @property
    def quiz_score_percentage(self):
        """Возвращает процент правильных ответов в квизе"""
        if not self.quiz_total_questions:
            return None
        return (self.quiz_correct_answers / self.quiz_total_questions) * 100


class UserQuizAnswer(BaseModel):
    """
    Ответ пользователя на вопрос квиза
    """
    user_flow = models.ForeignKey(
        UserFlow,
        on_delete=models.CASCADE,
        related_name='quiz_answers',
        verbose_name='Прохождение потока'
    )
    question = models.ForeignKey(
        QuizQuestion,
        on_delete=models.CASCADE,
        related_name='user_answers',
        verbose_name='Вопрос'
    )
    selected_answer = models.ForeignKey(
        QuizAnswer,
        on_delete=models.CASCADE,
        related_name='user_selections',
        verbose_name='Выбранный ответ'
    )
    is_correct = models.BooleanField(
        'Правильный ответ',
        help_text='Был ли ответ правильным'
    )
    answered_at = models.DateTimeField(
        'Время ответа',
        default=timezone.now
    )
    
    class Meta:
        db_table = 'user_quiz_answers'
        verbose_name = 'Ответ пользователя на квиз'
        verbose_name_plural = 'Ответы пользователей на квизы'
        unique_together = [('user_flow', 'question')]
        indexes = [
            models.Index(fields=['user_flow', 'is_correct']),
            models.Index(fields=['question', 'is_correct']),
        ]
    
    def __str__(self):
        return f"{self.user_flow.user.name} - {self.question}"


class FlowAction(BaseModel):
    """
    История действий с потоком (для аудита)
    """
    class ActionType(models.TextChoices):
        STARTED = 'started', 'Запущен'
        PAUSED = 'paused', 'Приостановлен'
        RESUMED = 'resumed', 'Возобновлен'
        COMPLETED = 'completed', 'Завершен'
        EXTENDED_DEADLINE = 'extended_deadline', 'Продлен дедлайн'
        STEP_COMPLETED = 'step_completed', 'Этап завершен'
        QUIZ_PASSED = 'quiz_passed', 'Квиз пройден'
        TASK_COMPLETED = 'task_completed', 'Задание выполнено'
    
    user_flow = models.ForeignKey(
        UserFlow,
        on_delete=models.CASCADE,
        related_name='actions',
        verbose_name='Прохождение потока'
    )
    action_type = models.CharField(
        'Тип действия',
        max_length=30,
        choices=ActionType.choices,
        help_text='Тип выполненного действия'
    )
    performed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='performed_flow_actions',
        verbose_name='Выполнил'
    )
    reason = models.TextField(
        'Причина',
        null=True,
        blank=True,
        help_text='Причина выполнения действия'
    )
    metadata = models.JSONField(
        'Метаданные',
        default=dict,
        blank=True,
        help_text='Дополнительная информация о действии'
    )
    performed_at = models.DateTimeField(
        'Время выполнения',
        default=timezone.now
    )
    
    class Meta:
        db_table = 'flow_actions'
        verbose_name = 'Действие с потоком'
        verbose_name_plural = 'Действия с потоками'
        ordering = ['-performed_at']
        indexes = [
            models.Index(fields=['user_flow', 'action_type']),
            models.Index(fields=['performed_by', 'performed_at']),
        ]
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.user_flow}"