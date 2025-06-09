"""
Административная панель для статей и гайдов
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count

from .models import ArticleCategory, Article, ArticleReview, ArticleView, ArticleBookmark


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    """
    Административная панель для категорий статей
    """
    list_display = [
        'name', 'parent_display', 'articles_count', 
        'order', 'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['slug', 'created_at', 'updated_at', 'full_path']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description', 'parent')
        }),
        ('Настройки', {
            'fields': ('order', 'is_active')
        }),
        ('Служебная информация', {
            'fields': ('full_path', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def parent_display(self, obj):
        """Отображение родительской категории"""
        if obj.parent:
            url = reverse('admin:guides_articlecategory_change', args=[obj.parent.id])
            return format_html('<a href="{}">{}</a>', url, obj.parent.name)
        return '-'
    parent_display.short_description = 'Родительская категория'
    
    def articles_count(self, obj):
        """Количество статей в категории"""
        count = obj.articles.filter(is_active=True, is_published=True).count()
        if count > 0:
            url = reverse('admin:guides_article_changelist') + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return 0
    articles_count.short_description = 'Статей'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent').annotate(
            articles_count=Count('articles', filter=models.Q(articles__is_active=True))
        )


class ArticleReviewInline(admin.TabularInline):
    """
    Инлайн для рецензий статей
    """
    model = ArticleReview
    extra = 0
    fields = ['reviewer', 'status', 'comments', 'reviewed_at']
    readonly_fields = ['reviewed_at']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    Административная панель для статей
    """
    list_display = [
        'title', 'author_name', 'category_name', 'article_type',
        'difficulty_level', 'is_published_display', 'view_count',
        'reading_time_minutes', 'published_at'
    ]
    list_filter = [
        'is_published', 'article_type', 'difficulty_level', 
        'category', 'author', 'created_at', 'published_at'
    ]
    search_fields = ['title', 'summary', 'content', 'tags']
    readonly_fields = [
        'slug', 'view_count', 'published_at', 'version',
        'is_used_in_flows', 'created_at', 'updated_at'
    ]
    prepopulated_fields = {'slug': ('title',)}
    # Связь с рецензентами реализована через промежуточную модель,
    # поэтому поле `reviewers` не добавляется напрямую в форму статьи
    filter_horizontal = []
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'summary', 'content')
        }),
        ('Классификация', {
            'fields': ('article_type', 'category', 'tags', 'difficulty_level')
        }),
        ('Авторство', {
            'fields': ('author',)
        }),
        ('Метаданные', {
            'fields': ('reading_time_minutes', 'version', 'previous_version')
        }),
        ('Публикация', {
            'fields': ('is_published', 'published_at', 'is_active')
        }),
        ('Статистика', {
            'fields': ('view_count', 'is_used_in_flows'),
            'classes': ('collapse',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ArticleReviewInline]
    
    def author_name(self, obj):
        """Имя автора"""
        if obj.author:
            url = reverse('admin:users_user_change', args=[obj.author.id])
            return format_html('<a href="{}">{}</a>', url, obj.author.name)
        return '-'
    author_name.short_description = 'Автор'
    author_name.admin_order_field = 'author__name'
    
    def category_name(self, obj):
        """Название категории"""
        if obj.category:
            url = reverse('admin:guides_articlecategory_change', args=[obj.category.id])
            return format_html('<a href="{}">{}</a>', url, obj.category.name)
        return '-'
    category_name.short_description = 'Категория'
    category_name.admin_order_field = 'category__name'
    
    def is_published_display(self, obj):
        """Статус публикации"""
        if obj.is_published:
            return format_html('<span style="color: green;">Опубликована</span>')
        return format_html('<span style="color: red;">Черновик</span>')
    is_published_display.short_description = 'Статус'
    is_published_display.admin_order_field = 'is_published'
    
    def save_model(self, request, obj, form, change):
        """Устанавливаем автора при создании"""
        if not change and not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category')
    
    actions = ['publish_articles', 'unpublish_articles']
    
    def publish_articles(self, request, queryset):
        """Массовая публикация статей"""
        from django.utils import timezone
        updated = queryset.update(is_published=True, published_at=timezone.now())
        self.message_user(request, f'Опубликовано {updated} статей.')
    publish_articles.short_description = 'Опубликовать выбранные статьи'
    
    def unpublish_articles(self, request, queryset):
        """Массовое снятие с публикации"""
        updated = queryset.update(is_published=False, published_at=None)
        self.message_user(request, f'Сняты с публикации {updated} статей.')
    unpublish_articles.short_description = 'Снять с публикации выбранные статьи'


@admin.register(ArticleReview)
class ArticleReviewAdmin(admin.ModelAdmin):
    """
    Административная панель для рецензий статей
    """
    list_display = [
        'article_title', 'reviewer_name', 'status', 
        'reviewed_at', 'created_at'
    ]
    list_filter = ['status', 'reviewed_at', 'created_at']
    search_fields = ['article__title', 'reviewer__name', 'comments']
    readonly_fields = ['reviewed_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Рецензия', {
            'fields': ('article', 'reviewer', 'status')
        }),
        ('Комментарии', {
            'fields': ('comments',)
        }),
        ('Временные метки', {
            'fields': ('reviewed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def article_title(self, obj):
        """Название статьи"""
        url = reverse('admin:guides_article_change', args=[obj.article.id])
        return format_html('<a href="{}">{}</a>', url, obj.article.title)
    article_title.short_description = 'Статья'
    article_title.admin_order_field = 'article__title'
    
    def reviewer_name(self, obj):
        """Имя рецензента"""
        url = reverse('admin:users_user_change', args=[obj.reviewer.id])
        return format_html('<a href="{}">{}</a>', url, obj.reviewer.name)
    reviewer_name.short_description = 'Рецензент'
    reviewer_name.admin_order_field = 'reviewer__name'
    
    def save_model(self, request, obj, form, change):
        """Устанавливаем рецензента и время при изменении статуса"""
        if not change:
            obj.reviewer = request.user
        
        if 'status' in form.changed_data and obj.status != 'pending':
            from django.utils import timezone
            obj.reviewed_at = timezone.now()
        
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('article', 'reviewer')


@admin.register(ArticleView)
class ArticleViewAdmin(admin.ModelAdmin):
    """
    Административная панель для просмотров статей
    """
    list_display = [
        'article_title', 'user_name', 'flow_step_display',
        'reading_time_display', 'viewed_at'
    ]
    list_filter = ['viewed_at', 'article', 'flow_step']
    search_fields = ['article__title', 'user__name']
    readonly_fields = ['viewed_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Просмотр', {
            'fields': ('article', 'user', 'flow_step', 'reading_time_seconds')
        }),
        ('Временные метки', {
            'fields': ('viewed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def article_title(self, obj):
        """Название статьи"""
        return obj.article.title
    article_title.short_description = 'Статья'
    article_title.admin_order_field = 'article__title'
    
    def user_name(self, obj):
        """Имя пользователя"""
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.name)
    user_name.short_description = 'Пользователь'
    user_name.admin_order_field = 'user__name'
    
    def flow_step_display(self, obj):
        """Этап потока"""
        if obj.flow_step:
            return f"{obj.flow_step.flow.title} - {obj.flow_step.title}"
        return '-'
    flow_step_display.short_description = 'Этап потока'
    
    def reading_time_display(self, obj):
        """Время чтения в удобном формате"""
        if obj.reading_time_seconds:
            minutes = obj.reading_time_seconds // 60
            seconds = obj.reading_time_seconds % 60
            return f"{minutes}м {seconds}с"
        return '-'
    reading_time_display.short_description = 'Время чтения'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'article', 'user', 'flow_step__flow'
        )
    
    def has_add_permission(self, request):
        """Запрещаем ручное создание просмотров"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Запрещаем редактирование просмотров"""
        return False


@admin.register(ArticleBookmark)
class ArticleBookmarkAdmin(admin.ModelAdmin):
    """
    Административная панель для закладок статей
    """
    list_display = ['article_title', 'user_name', 'note_preview', 'created_at']
    list_filter = ['created_at', 'article__category']
    search_fields = ['article__title', 'user__name', 'note']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Закладка', {
            'fields': ('article', 'user', 'note')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def article_title(self, obj):
        """Название статьи"""
        url = reverse('admin:guides_article_change', args=[obj.article.id])
        return format_html('<a href="{}">{}</a>', url, obj.article.title)
    article_title.short_description = 'Статья'
    article_title.admin_order_field = 'article__title'
    
    def user_name(self, obj):
        """Имя пользователя"""
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.name)
    user_name.short_description = 'Пользователь'
    user_name.admin_order_field = 'user__name'
    
    def note_preview(self, obj):
        """Превью заметки"""
        if obj.note:
            return obj.note[:50] + '...' if len(obj.note) > 50 else obj.note
        return '-'
    note_preview.short_description = 'Заметка'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('article', 'user')


# Дополнительные настройки админки
from django.contrib import admin

# Настройка отображения количества записей на странице
admin.site.list_per_page = 25

# Добавляем кастомные фильтры
class PublishedFilter(admin.SimpleListFilter):
    """Фильтр для опубликованных статей"""
    title = 'статус публикации'
    parameter_name = 'published'
    
    def lookups(self, request, model_admin):
        return (
            ('yes', 'Опубликованные'),
            ('no', 'Черновики'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(is_published=True)
        if self.value() == 'no':
            return queryset.filter(is_published=False)

# Применяем фильтр к модели Article
ArticleAdmin.list_filter = list(ArticleAdmin.list_filter) + [PublishedFilter]