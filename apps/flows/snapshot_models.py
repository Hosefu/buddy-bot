"""
Модели для сохранения снапшотов контента на момент прохождения
"""
from django.db import models
from django.utils import timezone
from apps.common.models import BaseModel


class BaseSnapshotModel(BaseModel):
    """
    Базовая модель для всех снапшотов
    """
    snapshot_created_at = models.DateTimeField(
        'Время создания снапшота',
        default=timezone.now,
        help_text='Когда был создан этот снапшот'
    )
    
    # Версия контента на момент снапшота
    content_version = models.CharField(
        'Версия контента',
        max_length=50,
        default='1.0',
        help_text='Версия контента на момент создания снапшота'
    )
    
    class Meta:
        abstract = True


class TaskSnapshot(BaseSnapshotModel):
    """
    Снапшот задания на момент выполнения пользователем
    """
    user_step_progress = models.OneToOneField(
        'flows.UserStepProgress',
        on_delete=models.CASCADE,
        related_name='task_snapshot',
        verbose_name='Прогресс по этапу'
    )
    
    # Снапшот данных задания
    task_title = models.CharField('Название задания', max_length=255)
    task_description = models.TextField('Описание задания')
    task_instruction = models.TextField('Инструкция', blank=True, null=True)
    task_code_word = models.CharField('Кодовое слово', max_length=100)
    task_hint = models.TextField('Подсказка', blank=True, null=True)
    
    # Ответ пользователя
    user_answer = models.CharField('Ответ пользователя', max_length=255)
    is_correct = models.BooleanField('Правильный ответ')
    attempts_count = models.PositiveIntegerField('Количество попыток', default=1)
    
    class Meta:
        db_table = 'task_snapshots'
        verbose_name = 'Снапшот задания'
        verbose_name_plural = 'Снапшоты заданий'
    
    def __str__(self):
        return f"Снапшот: {self.task_title} - {self.user_step_progress.user_flow.user.name}"


class QuizSnapshot(BaseSnapshotModel):
    """
    Снапшот квиза на момент прохождения пользователем
    """
    user_step_progress = models.OneToOneField(
        'flows.UserStepProgress',
        on_delete=models.CASCADE,
        related_name='quiz_snapshot',
        verbose_name='Прогресс по этапу'
    )
    
    # Снапшот данных квиза
    quiz_title = models.CharField('Название квиза', max_length=255)
    quiz_description = models.TextField('Описание квиза', blank=True)
    passing_score_percentage = models.PositiveIntegerField('Проходной балл (%)')
    
    # Результаты прохождения
    total_questions = models.PositiveIntegerField('Всего вопросов')
    correct_answers = models.PositiveIntegerField('Правильных ответов')
    score_percentage = models.PositiveIntegerField('Процент правильных ответов')
    is_passed = models.BooleanField('Квиз пройден')
    
    class Meta:
        db_table = 'quiz_snapshots'
        verbose_name = 'Снапшот квиза'
        verbose_name_plural = 'Снапшоты квизов'
    
    def __str__(self):
        return f"Снапшот: {self.quiz_title} - {self.user_step_progress.user_flow.user.name}"


class QuizQuestionSnapshot(BaseSnapshotModel):
    """
    Снапшот вопроса квиза на момент прохождения
    """
    quiz_snapshot = models.ForeignKey(
        QuizSnapshot,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Снапшот квиза'
    )
    
    # Снапшот данных вопроса (на момент прохождения)
    original_question_id = models.PositiveIntegerField('ID оригинального вопроса')
    question_text = models.TextField('Текст вопроса')
    question_order = models.PositiveIntegerField('Порядок вопроса')
    explanation = models.TextField('Объяснение', blank=True)
    
    class Meta:
        db_table = 'quiz_question_snapshots'
        verbose_name = 'Снапшот вопроса квиза'
        verbose_name_plural = 'Снапшоты вопросов квизов'
        ordering = ['question_order']
    
    def __str__(self):
        return f"Вопрос {self.question_order}: {self.question_text[:50]}..."


class QuizAnswerSnapshot(BaseSnapshotModel):
    """
    Снапшот варианта ответа на момент прохождения
    """
    question_snapshot = models.ForeignKey(
        QuizQuestionSnapshot,
        on_delete=models.CASCADE,
        related_name='answer_options',
        verbose_name='Снапшот вопроса'
    )
    
    # Снапшот данных ответа (на момент прохождения)
    original_answer_id = models.PositiveIntegerField('ID оригинального ответа')
    answer_text = models.TextField('Текст ответа')
    is_correct = models.BooleanField('Правильный ответ')
    answer_order = models.PositiveIntegerField('Порядок ответа')
    explanation = models.TextField('Объяснение ответа', blank=True)
    
    class Meta:
        db_table = 'quiz_answer_snapshots'
        verbose_name = 'Снапшот ответа'
        verbose_name_plural = 'Снапшоты ответов'
        ordering = ['answer_order']
    
    def __str__(self):
        return f"Ответ: {self.answer_text[:30]}..."


class UserQuizAnswerSnapshot(BaseSnapshotModel):
    """
    Снапшот ответа пользователя (замена UserQuizAnswer)
    """
    quiz_snapshot = models.ForeignKey(
        QuizSnapshot,
        on_delete=models.CASCADE,
        related_name='user_answers',
        verbose_name='Снапшот квиза'
    )
    question_snapshot = models.ForeignKey(
        QuizQuestionSnapshot,
        on_delete=models.CASCADE,
        related_name='user_answer',
        verbose_name='Снапшот вопроса'
    )
    selected_answer_snapshot = models.ForeignKey(
        QuizAnswerSnapshot,
        on_delete=models.CASCADE,
        related_name='user_selections',
        verbose_name='Выбранный ответ (снапшот)'
    )
    
    # Результат ответа
    is_correct = models.BooleanField('Ответ правильный')
    answered_at = models.DateTimeField('Время ответа', default=timezone.now)
    
    class Meta:
        db_table = 'user_quiz_answer_snapshots'
        verbose_name = 'Ответ пользователя (снапшот)'
        verbose_name_plural = 'Ответы пользователей (снапшоты)'
        unique_together = [('quiz_snapshot', 'question_snapshot')]
    
    def __str__(self):
        return f"{self.quiz_snapshot.user_step_progress.user_flow.user.name} - {self.question_snapshot.question_text[:30]}..."


class ArticleSnapshot(BaseSnapshotModel):
    """
    Снапшот статьи на момент прочтения пользователем
    """
    user_step_progress = models.OneToOneField(
        'flows.UserStepProgress',
        on_delete=models.CASCADE,
        related_name='article_snapshot',
        verbose_name='Прогресс по этапу'
    )
    
    # Снапшот данных статьи
    article_title = models.CharField('Название статьи', max_length=255)
    article_content = models.TextField('Содержание статьи')
    article_summary = models.TextField('Краткое описание', blank=True)
    
    # Время чтения
    reading_started_at = models.DateTimeField('Начало чтения', default=timezone.now)
    reading_time_seconds = models.PositiveIntegerField('Время чтения (сек)', default=0)
    
    class Meta:
        db_table = 'article_snapshots'
        verbose_name = 'Снапшот статьи'
        verbose_name_plural = 'Снапшоты статей'
    
    def __str__(self):
        return f"Снапшот: {self.article_title} - {self.user_step_progress.user_flow.user.name}" 