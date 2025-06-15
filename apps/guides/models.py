"""
Модели для системы статей и гайдов
"""
from django.db import models
from django.utils.text import slugify
from django.urls import reverse

from apps.common.models import BaseModel, ActiveModel
from apps.users.models import User
from .managers import ArticleManager


class ArticleCategory(BaseModel, ActiveModel):
    """
    Категория статей для организации контента
    """
    name = models.CharField(
        'Название категории',
        max_length=100,
        unique=True,
        help_text='Название категории статей'
    )
    slug = models.SlugField(
        'URL slug',
        max_length=100,
        unique=True,
        help_text='URL-friendly название категории'
    )
    description = models.TextField(
        'Описание',
        blank=True,
        help_text='Описание категории'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name='Родительская категория',
        help_text='Родительская категория для создания иерархии'
    )
    order = models.PositiveIntegerField(
        'Порядок сортировки',
        default=0,
        help_text='Порядок отображения категорий'
    )
    
    class Meta:
        db_table = 'article_categories'
        verbose_name = 'Категория статей'
        verbose_name_plural = 'Категории статей'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Автоматически генерирует slug при сохранении"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def full_path(self):
        """Возвращает полный путь категории с родителями"""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name
    
    def get_all_subcategories(self):
        """Возвращает все подкатегории рекурсивно"""
        subcategories = list(self.subcategories.filter(is_active=True))
        for subcategory in self.subcategories.filter(is_active=True):
            subcategories.extend(subcategory.get_all_subcategories())
        return subcategories


class Article(BaseModel, ActiveModel):
    """
    Статья - основной контент системы
    Может использоваться как самостоятельно, так и в составе потоков обучения
    """
    class ArticleType(models.TextChoices):
        GUIDE = 'guide', 'Руководство'
        FAQ = 'faq', 'FAQ'
        POLICY = 'policy', 'Политика'
        PROCEDURE = 'procedure', 'Процедура'
        REFERENCE = 'reference', 'Справочник'
        NEWS = 'news', 'Новость'
    
    # Основная информация
    title = models.CharField(
        'Заголовок',
        max_length=255,
        help_text='Заголовок статьи'
    )
    slug = models.SlugField(
        'URL slug',
        max_length=255,
        unique=True,
        help_text='URL-friendly название статьи'
    )
    summary = models.TextField(
        'Краткое описание',
        max_length=500,
        help_text='Краткое описание содержания статьи'
    )
    content = models.TextField(
        'Содержание',
        help_text='Основное содержание статьи в формате Markdown'
    )

    flow_step = models.OneToOneField(
        'flows.FlowStep',
        on_delete=models.CASCADE,
        related_name='article',
        verbose_name='Этап потока',
        null=True,
        blank=True,
        help_text='Связанный этап потока'
    )
    
    # Классификация
    article_type = models.CharField(
        'Тип статьи',
        max_length=20,
        choices=ArticleType.choices,
        default=ArticleType.GUIDE,
        help_text='Тип статьи для организации контента'
    )
    category = models.ForeignKey(
        ArticleCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
        verbose_name='Категория',
        help_text='Категория статьи'
    )
    tags = models.JSONField(
        'Теги',
        default=list,
        blank=True,
        help_text='Список тегов для поиска и фильтрации'
    )
    
    # Авторство и модерация
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='authored_articles',
        verbose_name='Автор',
        help_text='Автор статьи'
    )
    reviewers = models.ManyToManyField(
        User,
        through='ArticleReview',
        related_name='reviewed_articles',
        blank=True,
        verbose_name='Рецензенты'
    )
    
    # Метаданные
    reading_time_minutes = models.PositiveIntegerField(
        'Время чтения (минуты)',
        null=True,
        blank=True,
        help_text='Приблизительное время чтения статьи'
    )
    difficulty_level = models.CharField(
        'Уровень сложности',
        max_length=20,
        choices=[
            ('beginner', 'Начальный'),
            ('intermediate', 'Средний'),
            ('advanced', 'Продвинутый'),
        ],
        default='beginner',
        help_text='Уровень сложности статьи'
    )
    
    # Публикация
    is_published = models.BooleanField(
        'Опубликована',
        default=False,
        help_text='Опубликована ли статья'
    )
    published_at = models.DateTimeField(
        'Дата публикации',
        null=True,
        blank=True,
        help_text='Дата и время публикации статьи'
    )
    
    # Версионирование
    version = models.CharField(
        'Версия',
        max_length=20,
        default='1.0',
        help_text='Версия статьи'
    )
    previous_version = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='newer_versions',
        verbose_name='Предыдущая версия'
    )
    
    # Статистика (денормализованные данные для производительности)
    view_count = models.PositiveIntegerField(
        'Количество просмотров',
        default=0,
        help_text='Общее количество просмотров статьи'
    )
    
    objects = ArticleManager()
    
    class Meta:
        db_table = 'articles'
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['is_published', 'is_active']),
            models.Index(fields=['category', 'is_published']),
            models.Index(fields=['article_type', 'is_published']),
            models.Index(fields=['author', 'is_published']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Автоматически генерирует slug и устанавливает время чтения"""
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Автоматический расчет времени чтения (примерно 200 слов в минуту)
        if self.content and not self.reading_time_minutes:
            word_count = len(self.content.split())
            self.reading_time_minutes = max(1, word_count // 200)
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Возвращает URL статьи"""
        return reverse('guides:article-detail', kwargs={'slug': self.slug})
    
    @property
    def is_used_in_flows(self):
        """Проверяет, используется ли статья в потоках обучения"""
        return hasattr(self, 'flow_step') and self.flow_step is not None and self.flow_step.is_active
    
    def increment_view_count(self):
        """Увеличивает счетчик просмотров"""
        self.view_count = models.F('view_count') + 1
        self.save(update_fields=['view_count'])
    
    def create_new_version(self, **updated_data):
        """Создает новую версию статьи"""
        # Сохраняем текущую версию как предыдущую
        previous_version = self
        
        # Создаем новую версию
        self.pk = None
        self.previous_version = previous_version
        
        # Обновляем версию
        version_parts = previous_version.version.split('.')
        if len(version_parts) == 2:
            major, minor = int(version_parts[0]), int(version_parts[1])
            self.version = f"{major}.{minor + 1}"
        else:
            self.version = "1.1"
        
        # Применяем обновления
        for field, value in updated_data.items():
            setattr(self, field, value)
        
        # Сбрасываем публикацию для модерации
        self.is_published = False
        self.published_at = None
        
        self.save()
        return self


class ArticleReview(BaseModel):
    """
    Рецензия на статью
    """
    class ReviewStatus(models.TextChoices):
        PENDING = 'pending', 'Ожидает рецензии'
        APPROVED = 'approved', 'Одобрена'
        REJECTED = 'rejected', 'Отклонена'
        NEEDS_CHANGES = 'needs_changes', 'Требует изменений'
    
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Статья'
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='article_reviews',
        verbose_name='Рецензент'
    )
    status = models.CharField(
        'Статус рецензии',
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
        help_text='Статус рецензии'
    )
    comments = models.TextField(
        'Комментарии',
        blank=True,
        help_text='Комментарии рецензента'
    )
    reviewed_at = models.DateTimeField(
        'Дата рецензии',
        null=True,
        blank=True,
        help_text='Дата завершения рецензии'
    )
    
    class Meta:
        db_table = 'article_reviews'
        verbose_name = 'Рецензия статьи'
        verbose_name_plural = 'Рецензии статей'
        unique_together = [('article', 'reviewer')]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Рецензия {self.reviewer.name} на {self.article.title}"


class ArticleView(BaseModel):
    """
    Просмотр статьи пользователем (для аналитики)
    """
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='article_views',
        verbose_name='Статья'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='article_views',
        verbose_name='Пользователь'
    )
    flow_step = models.ForeignKey(
        'flows.FlowStep',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='article_views',
        verbose_name='Этап потока',
        help_text='Этап потока, в рамках которого была просмотрена статья'
    )
    reading_time_seconds = models.PositiveIntegerField(
        'Время чтения (секунды)',
        null=True,
        blank=True,
        help_text='Фактическое время чтения статьи пользователем'
    )
    viewed_at = models.DateTimeField(
        'Время просмотра',
        auto_now_add=True
    )
    
    class Meta:
        db_table = 'article_views'
        verbose_name = 'Просмотр статьи'
        verbose_name_plural = 'Просмотры статей'
        indexes = [
            models.Index(fields=['article', 'user']),
            models.Index(fields=['user', 'viewed_at']),
            models.Index(fields=['flow_step', 'viewed_at']),
        ]
    
    def __str__(self):
        return f"{self.user.name} просмотрел {self.article.title}"


class ArticleBookmark(BaseModel):
    """
    Закладка статьи пользователем
    """
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        verbose_name='Статья'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookmarked_articles',
        verbose_name='Пользователь'
    )
    note = models.TextField(
        'Заметка',
        blank=True,
        help_text='Личная заметка пользователя к закладке'
    )
    
    class Meta:
        db_table = 'article_bookmarks'
        verbose_name = 'Закладка статьи'
        verbose_name_plural = 'Закладки статей'
        unique_together = [('article', 'user')]
    
    def __str__(self):
        return f"{self.user.name} добавил в закладки {self.article.title}"