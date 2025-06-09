"""
Менеджеры для моделей статей и гайдов
"""
from django.db import models
from django.utils import timezone


class ArticleManager(models.Manager):
    """
    Менеджер для модели Article
    Предоставляет методы для работы со статьями
    """
    
    def active(self):
        """
        Возвращает только активные статьи
        
        Returns:
            QuerySet: Активные статьи
        """
        return self.filter(is_active=True, is_deleted=False)
    
    def published(self):
        """
        Возвращает только опубликованные статьи
        
        Returns:
            QuerySet: Опубликованные статьи
        """
        return self.active().filter(
            is_published=True,
            published_at__lte=timezone.now()
        )
    
    def draft(self):
        """
        Возвращает черновики статей
        
        Returns:
            QuerySet: Неопубликованные статьи
        """
        return self.active().filter(is_published=False)
    
    def by_category(self, category):
        """
        Возвращает статьи определенной категории
        
        Args:
            category (ArticleCategory or str): Категория или её slug
            
        Returns:
            QuerySet: Статьи указанной категории
        """
        if isinstance(category, str):
            return self.published().filter(category__slug=category)
        return self.published().filter(category=category)
    
    def by_type(self, article_type):
        """
        Возвращает статьи определенного типа
        
        Args:
            article_type (str): Тип статьи
            
        Returns:
            QuerySet: Статьи указанного типа
        """
        return self.published().filter(article_type=article_type)
    
    def by_author(self, author):
        """
        Возвращает статьи конкретного автора
        
        Args:
            author (User): Автор статей
            
        Returns:
            QuerySet: Статьи автора
        """
        return self.published().filter(author=author)
    
    def search(self, query):
        """
        Поиск статей по заголовку, содержанию и тегам
        
        Args:
            query (str): Поисковый запрос
            
        Returns:
            QuerySet: Найденные статьи
        """
        return self.published().filter(
            models.Q(title__icontains=query) |
            models.Q(summary__icontains=query) |
            models.Q(content__icontains=query) |
            models.Q(tags__contains=[query])
        ).distinct()
    
    def popular(self, limit=10):
        """
        Возвращает популярные статьи по количеству просмотров
        
        Args:
            limit (int): Количество статей
            
        Returns:
            QuerySet: Популярные статьи
        """
        return self.published().order_by('-view_count')[:limit]
    
    def recent(self, limit=10):
        """
        Возвращает недавно опубликованные статьи
        
        Args:
            limit (int): Количество статей
            
        Returns:
            QuerySet: Недавние статьи
        """
        return self.published().order_by('-published_at')[:limit]
    
    def by_difficulty(self, level):
        """
        Возвращает статьи определенного уровня сложности
        
        Args:
            level (str): Уровень сложности
            
        Returns:
            QuerySet: Статьи указанного уровня
        """
        return self.published().filter(difficulty_level=level)
    
    def for_flow_steps(self):
        """
        Возвращает статьи, используемые в потоках обучения
        
        Returns:
            QuerySet: Статьи, используемые в потоках
        """
        return self.published().filter(
            flow_steps__is_active=True
        ).distinct()
    
    def standalone(self):
        """
        Возвращает самостоятельные статьи (не используемые в потоках)
        
        Returns:
            QuerySet: Самостоятельные статьи
        """
        return self.published().exclude(
            flow_steps__is_active=True
        )
    
    def with_statistics(self):
        """
        Возвращает статьи с подсчитанной статистикой
        
        Returns:
            QuerySet: Статьи с аннотированной статистикой
        """
        return self.published().annotate(
            total_views=models.Count('article_views'),
            unique_readers=models.Count('article_views__user', distinct=True),
            bookmarks_count=models.Count('bookmarks'),
            avg_reading_time=models.Avg('article_views__reading_time_seconds'),
            flow_usage_count=models.Count('flow_steps', distinct=True)
        )
    
    def requiring_review(self):
        """
        Возвращает статьи, требующие рецензии
        
        Returns:
            QuerySet: Статьи на рецензии
        """
        return self.active().filter(
            is_published=False,
            reviews__status='pending'
        ).distinct()
    
    def by_tags(self, tags):
        """
        Возвращает статьи с указанными тегами
        
        Args:
            tags (list): Список тегов
            
        Returns:
            QuerySet: Статьи с указанными тегами
        """
        query = models.Q()
        for tag in tags:
            query |= models.Q(tags__contains=[tag])
        return self.published().filter(query).distinct()
    
    def outdated(self, days=365):
        """
        Возвращает устаревшие статьи (не обновлялись долгое время)
        
        Args:
            days (int): Количество дней для определения устаревания
            
        Returns:
            QuerySet: Устаревшие статьи
        """
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=days)
        
        return self.published().filter(
            updated_at__lt=cutoff_date
        ).order_by('updated_at')
    
    def get_related_articles(self, article, limit=5):
        """
        Возвращает связанные статьи (по категории и тегам)
        
        Args:
            article (Article): Статья для поиска связанных
            limit (int): Количество связанных статей
            
        Returns:
            QuerySet: Связанные статьи
        """
        related = self.published().exclude(id=article.id)
        
        # Приоритет: статьи той же категории
        if article.category:
            category_articles = related.filter(category=article.category)
            if category_articles.exists():
                related = category_articles
        
        # Дополнительно фильтруем по тегам если есть
        if article.tags:
            tag_query = models.Q()
            for tag in article.tags:
                tag_query |= models.Q(tags__contains=[tag])
            tagged_articles = related.filter(tag_query)
            if tagged_articles.exists():
                related = tagged_articles
        
        return related.order_by('-published_at')[:limit]