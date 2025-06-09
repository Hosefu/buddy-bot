"""
Сериализаторы для статей и гайдов
"""
from rest_framework import serializers
from django.utils import timezone

from .models import ArticleCategory, Article, ArticleReview, ArticleView, ArticleBookmark
from apps.users.serializers import UserListSerializer


class ArticleCategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор категории статей
    """
    full_path = serializers.ReadOnlyField()
    subcategories_count = serializers.SerializerMethodField()
    articles_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ArticleCategory
        fields = [
            'id', 'name', 'slug', 'description', 'parent',
            'order', 'is_active', 'full_path', 'subcategories_count',
            'articles_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_subcategories_count(self, obj):
        """Количество подкategorий"""
        return obj.subcategories.filter(is_active=True).count()
    
    def get_articles_count(self, obj):
        """Количество статей в категории"""
        return obj.articles.filter(is_active=True, is_published=True).count()


class ArticleCategoryTreeSerializer(ArticleCategorySerializer):
    """
    Сериализатор категории с подкategориями (древовидная структура)
    """
    subcategories = serializers.SerializerMethodField()
    
    class Meta(ArticleCategorySerializer.Meta):
        fields = ArticleCategorySerializer.Meta.fields + ['subcategories']
    
    def get_subcategories(self, obj):
        """Рекурсивно получаем подкategории"""
        subcategories = obj.subcategories.filter(is_active=True).order_by('order', 'name')
        return ArticleCategoryTreeSerializer(subcategories, many=True, context=self.context).data


class ArticleBasicSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор статьи (краткая информация)
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    author_name = serializers.CharField(source='author.name', read_only=True)
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'summary', 'article_type',
            'category_name', 'author_name', 'reading_time_minutes',
            'difficulty_level', 'view_count', 'published_at'
        ]
        read_only_fields = ['id', 'slug', 'view_count', 'published_at']


class ArticleSerializer(serializers.ModelSerializer):
    """
    Полный сериализатор статьи
    """
    category = ArticleCategorySerializer(read_only=True)
    author = UserListSerializer(read_only=True)
    is_used_in_flows = serializers.ReadOnlyField()
    is_bookmarked = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'summary', 'content', 'article_type',
            'category', 'tags', 'author', 'reading_time_minutes',
            'difficulty_level', 'is_published', 'published_at',
            'version', 'view_count', 'is_used_in_flows', 'is_bookmarked',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'view_count', 'published_at', 'is_used_in_flows',
            'created_at', 'updated_at'
        ]
    
    def get_is_bookmarked(self, obj):
        """Проверяет, добавлена ли статья в закладки текущим пользователем"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ArticleBookmark.objects.filter(
                article=obj,
                user=request.user
            ).exists()
        return False


class ArticleCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания статьи
    """
    category_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Article
        fields = [
            'title', 'summary', 'content', 'article_type',
            'category_id', 'tags', 'difficulty_level'
        ]
    
    def validate_category_id(self, value):
        """Валидация категории"""
        if value:
            try:
                category = ArticleCategory.objects.get(id=value, is_active=True)
                return category
            except ArticleCategory.DoesNotExist:
                raise serializers.ValidationError("Категория не найдена")
        return None
    
    def create(self, validated_data):
        """Создание статьи"""
        category = validated_data.pop('category_id', None)
        validated_data['category'] = category
        validated_data['author'] = self.context['request'].user
        
        return Article.objects.create(**validated_data)


class ArticleUpdateSerializer(ArticleCreateSerializer):
    """
    Сериализатор для обновления статьи
    """
    def update(self, instance, validated_data):
        """Обновление статьи"""
        category = validated_data.pop('category_id', None)
        if category is not None:
            validated_data['category'] = category
        
        # При изменении опубликованной статьи сбрасываем публикацию
        if instance.is_published and any(
            field in validated_data for field in ['title', 'content', 'summary']
        ):
            validated_data['is_published'] = False
            validated_data['published_at'] = None
        
        return super().update(instance, validated_data)


class ArticleReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор рецензии статьи
    """
    reviewer = UserListSerializer(read_only=True)
    article_title = serializers.CharField(source='article.title', read_only=True)
    
    class Meta:
        model = ArticleReview
        fields = [
            'id', 'article_title', 'reviewer', 'status', 'comments',
            'reviewed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'reviewer', 'reviewed_at', 'created_at', 'updated_at'
        ]
    
    def update(self, instance, validated_data):
        """Обновление рецензии"""
        if 'status' in validated_data and validated_data['status'] != 'pending':
            validated_data['reviewed_at'] = timezone.now()
        
        return super().update(instance, validated_data)


class ArticleViewSerializer(serializers.ModelSerializer):
    """
    Сериализатор просмотра статьи
    """
    user = UserListSerializer(read_only=True)
    article_title = serializers.CharField(source='article.title', read_only=True)
    flow_step_title = serializers.CharField(source='flow_step.title', read_only=True)
    
    class Meta:
        model = ArticleView
        fields = [
            'id', 'article_title', 'user', 'flow_step_title',
            'reading_time_seconds', 'viewed_at'
        ]
        read_only_fields = ['id', 'user', 'viewed_at']


class ArticleBookmarkSerializer(serializers.ModelSerializer):
    """
    Сериализатор закладки статьи
    """
    article = ArticleBasicSerializer(read_only=True)
    user = UserListSerializer(read_only=True)
    
    class Meta:
        model = ArticleBookmark
        fields = [
            'id', 'article', 'user', 'note', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class ArticleBookmarkCreateSerializer(serializers.Serializer):
    """
    Сериализатор для добавления статьи в закладки
    """
    article_id = serializers.IntegerField()
    note = serializers.CharField(required=False, allow_blank=True)
    
    def validate_article_id(self, value):
        """Валидация статьи"""
        try:
            article = Article.objects.get(
                id=value,
                is_active=True,
                is_published=True
            )
            return article
        except Article.DoesNotExist:
            raise serializers.ValidationError("Статья не найдена")
    
    def validate(self, data):
        """Проверка дублирования закладки"""
        article = data['article_id']
        user = self.context['request'].user
        
        if ArticleBookmark.objects.filter(article=article, user=user).exists():
            raise serializers.ValidationError("Статья уже добавлена в закладки")
        
        return data
    
    def create(self, validated_data):
        """Создание закладки"""
        return ArticleBookmark.objects.create(
            article=validated_data['article_id'],
            user=self.context['request'].user,
            note=validated_data.get('note', '')
        )


class ArticleSearchSerializer(serializers.Serializer):
    """
    Сериализатор для поиска статей
    """
    query = serializers.CharField(required=False, allow_blank=True)
    category = serializers.CharField(required=False, allow_blank=True)
    article_type = serializers.CharField(required=False, allow_blank=True)
    difficulty_level = serializers.CharField(required=False, allow_blank=True)
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    author_id = serializers.IntegerField(required=False)
    
    def validate_category(self, value):
        """Валидация категории"""
        if value:
            if not ArticleCategory.objects.filter(
                slug=value,
                is_active=True
            ).exists():
                raise serializers.ValidationError("Категория не найдена")
        return value
    
    def validate_article_type(self, value):
        """Валидация типа статьи"""
        if value and value not in [choice[0] for choice in Article.ArticleType.choices]:
            raise serializers.ValidationError("Неверный тип статьи")
        return value
    
    def validate_difficulty_level(self, value):
        """Валидация уровня сложности"""
        valid_levels = ['beginner', 'intermediate', 'advanced']
        if value and value not in valid_levels:
            raise serializers.ValidationError("Неверный уровень сложности")
        return value


class ArticleStatisticsSerializer(serializers.Serializer):
    """
    Сериализатор статистики статей
    """
    total_articles = serializers.IntegerField()
    published_articles = serializers.IntegerField()
    draft_articles = serializers.IntegerField()
    total_views = serializers.IntegerField()
    unique_readers = serializers.IntegerField()
    avg_reading_time = serializers.FloatField()
    popular_categories = serializers.ListField()
    recent_articles = ArticleBasicSerializer(many=True)


class ArticleVersionSerializer(serializers.ModelSerializer):
    """
    Сериализатор версии статьи
    """
    author = UserListSerializer(read_only=True)
    changes_summary = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'summary', 'content', 'version',
            'author', 'changes_summary', 'created_at'
        ]
        read_only_fields = ['id', 'version', 'author', 'created_at']
    
    def create(self, validated_data):
        """Создание новой версии статьи"""
        original_article = self.context['original_article']
        changes_summary = validated_data.pop('changes_summary', '')
        
        # Создаем новую версию
        new_version = original_article.create_new_version(**validated_data)
        
        # Добавляем информацию об изменениях в метаданные
        if changes_summary:
            # Здесь можно добавить логику сохранения истории изменений
            pass
        
        return new_version


class PublishArticleSerializer(serializers.Serializer):
    """
    Сериализатор для публикации статьи
    """
    publish = serializers.BooleanField()
    
    def save(self, article):
        """Публикация или снятие с публикации статьи"""
        publish = self.validated_data['publish']
        
        if publish:
            article.is_published = True
            article.published_at = timezone.now()
        else:
            article.is_published = False
            article.published_at = None
        
        article.save()
        return article