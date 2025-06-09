"""
Представления для статей и гайдов
"""
from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

from .models import ArticleCategory, Article, ArticleReview, ArticleView, ArticleBookmark
from .serializers import (
    ArticleCategorySerializer, ArticleCategoryTreeSerializer,
    ArticleSerializer, ArticleBasicSerializer, ArticleCreateSerializer,
    ArticleUpdateSerializer, ArticleReviewSerializer, ArticleViewSerializer,
    ArticleBookmarkSerializer, ArticleBookmarkCreateSerializer,
    ArticleSearchSerializer, ArticleStatisticsSerializer,
    ArticleVersionSerializer, PublishArticleSerializer
)
from apps.common.permissions import (
    IsActiveUser, IsModerator, CanEditArticle, CanPublishArticle,
    IsAuthorOrReadOnly
)


class ArticleCategoryListView(generics.ListCreateAPIView):
    """
    Список категорий статей
    """
    serializer_class = ArticleCategorySerializer
    permission_classes = [IsActiveUser]
    
    def get_queryset(self):
        """Возвращает корневые категории"""
        return ArticleCategory.objects.filter(
            parent=None,
            is_active=True
        ).order_by('order', 'name')
    
    def get_permissions(self):
        """Создание категорий только для модераторов"""
        if self.request.method == 'POST':
            return [IsModerator()]
        return super().get_permissions()


class ArticleCategoryTreeView(generics.ListAPIView):
    """
    Древовидный список категорий
    """
    serializer_class = ArticleCategoryTreeSerializer
    permission_classes = [IsActiveUser]
    
    def get_queryset(self):
        return ArticleCategory.objects.filter(
            parent=None,
            is_active=True
        ).order_by('order', 'name')


class ArticleCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детали категории статей
    """
    queryset = ArticleCategory.objects.filter(is_active=True)
    serializer_class = ArticleCategorySerializer
    permission_classes = [IsActiveUser, IsModerator]
    lookup_field = 'slug'
    
    def perform_destroy(self, instance):
        """Мягкое удаление категории"""
        instance.delete()


class ArticleListView(generics.ListCreateAPIView):
    """
    Список статей с поиском и фильтрацией
    """
    permission_classes = [IsActiveUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['article_type', 'difficulty_level', 'category__slug']
    search_fields = ['title', 'summary', 'content']
    ordering_fields = ['published_at', 'view_count', 'title']
    ordering = ['-published_at']
    
    def get_queryset(self):
        """Возвращает опубликованные статьи или все для модераторов"""
        if self.request.user.has_role('moderator'):
            return Article.objects.active().select_related('author', 'category')
        return Article.objects.published().select_related('author', 'category')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ArticleCreateSerializer
        return ArticleBasicSerializer
    
    def get_permissions(self):
        """Создание статей для всех авторизованных"""
        if self.request.method == 'POST':
            return [IsActiveUser()]
        return super().get_permissions()


class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детали статьи
    """
    permission_classes = [IsActiveUser, CanEditArticle]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Доступ к статьям в зависимости от роли"""
        if self.request.user.has_role('moderator'):
            return Article.objects.active()
        return Article.objects.published()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ArticleUpdateSerializer
        return ArticleSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Увеличиваем счетчик просмотров при чтении"""
        instance = self.get_object()
        
        # Записываем просмотр
        ArticleView.objects.create(
            article=instance,
            user=request.user
        )
        
        # Увеличиваем счетчик
        instance.increment_view_count()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def perform_destroy(self, instance):
        """Мягкое удаление статьи"""
        instance.delete()


class ArticleSearchView(APIView):
    """
    Продвинутый поиск статей
    """
    permission_classes = [IsActiveUser]
    
    def get(self, request):
        """
        Поиск статей по различным критериям
        """
        serializer = ArticleSearchSerializer(data=request.query_params)
        
        if serializer.is_valid():
            queryset = Article.objects.published()
            data = serializer.validated_data
            
            # Текстовый поиск
            if data.get('query'):
                queryset = queryset.filter(
                    Q(title__icontains=data['query']) |
                    Q(summary__icontains=data['query']) |
                    Q(content__icontains=data['query'])
                )
            
            # Фильтр по категории
            if data.get('category'):
                queryset = queryset.filter(category__slug=data['category'])
            
            # Фильтр по типу
            if data.get('article_type'):
                queryset = queryset.filter(article_type=data['article_type'])
            
            # Фильтр по сложности
            if data.get('difficulty_level'):
                queryset = queryset.filter(difficulty_level=data['difficulty_level'])
            
            # Фильтр по тегам
            if data.get('tags'):
                for tag in data['tags']:
                    queryset = queryset.filter(tags__contains=[tag])
            
            # Фильтр по автору
            if data.get('author_id'):
                queryset = queryset.filter(author_id=data['author_id'])
            
            # Пагинация
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = ArticleBasicSerializer(page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)
            
            articles = queryset.select_related('author', 'category')[:50]  # Ограничиваем результат
            article_serializer = ArticleBasicSerializer(articles, many=True, context={'request': request})
            
            return Response({
                'count': queryset.count(),
                'results': article_serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticleBookmarkListView(generics.ListCreateAPIView):
    """
    Закладки пользователя
    """
    permission_classes = [IsActiveUser]
    
    def get_queryset(self):
        return ArticleBookmark.objects.filter(
            user=self.request.user
        ).select_related('article').order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ArticleBookmarkCreateSerializer
        return ArticleBookmarkSerializer


class ArticleBookmarkDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Управление закладкой
    """
    serializer_class = ArticleBookmarkSerializer
    permission_classes = [IsActiveUser]
    
    def get_queryset(self):
        return ArticleBookmark.objects.filter(user=self.request.user)


class PopularArticlesView(generics.ListAPIView):
    """
    Популярные статьи
    """
    serializer_class = ArticleBasicSerializer
    permission_classes = [IsActiveUser]
    
    def get_queryset(self):
        return Article.objects.popular(limit=20)


class RecentArticlesView(generics.ListAPIView):
    """
    Недавние статьи
    """
    serializer_class = ArticleBasicSerializer
    permission_classes = [IsActiveUser]
    
    def get_queryset(self):
        return Article.objects.recent(limit=20)


class RelatedArticlesView(generics.ListAPIView):
    """
    Связанные статьи
    """
    serializer_class = ArticleBasicSerializer
    permission_classes = [IsActiveUser]
    
    def get_queryset(self):
        article_slug = self.kwargs['slug']
        article = get_object_or_404(Article, slug=article_slug, is_published=True)
        return Article.objects.get_related_articles(article, limit=10)


# ========== Административные представления ==========

class AdminArticleListView(generics.ListAPIView):
    """
    Все статьи для модераторов
    """
    queryset = Article.objects.active().select_related('author', 'category')
    serializer_class = ArticleSerializer
    permission_classes = [IsModerator]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_published', 'article_type', 'author']
    search_fields = ['title', 'summary']
    ordering = ['-created_at']


class AdminArticleReviewListView(generics.ListCreateAPIView):
    """
    Рецензии статей
    """
    serializer_class = ArticleReviewSerializer
    permission_classes = [IsModerator]
    
    def get_queryset(self):
        article_id = self.kwargs.get('article_id')
        if article_id:
            return ArticleReview.objects.filter(article_id=article_id)
        return ArticleReview.objects.all().select_related('article', 'reviewer')
    
    def perform_create(self, serializer):
        article_id = self.kwargs['article_id']
        article = get_object_or_404(Article, id=article_id)
        serializer.save(
            article=article,
            reviewer=self.request.user
        )


class AdminArticleReviewDetailView(generics.RetrieveUpdateAPIView):
    """
    Управление рецензией
    """
    queryset = ArticleReview.objects.all()
    serializer_class = ArticleReviewSerializer
    permission_classes = [IsModerator]


class PublishArticleView(APIView):
    """
    Публикация/снятие с публикации статьи
    """
    permission_classes = [CanPublishArticle]
    
    def post(self, request, article_id):
        """
        Публикация или снятие с публикации статьи
        """
        article = get_object_or_404(Article, id=article_id)
        serializer = PublishArticleSerializer(data=request.data)
        
        if serializer.is_valid():
            updated_article = serializer.save(article)
            
            action = "опубликована" if updated_article.is_published else "снята с публикации"
            return Response({
                'message': f'Статья "{article.title}" {action}',
                'article': ArticleSerializer(updated_article, context={'request': request}).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticleVersionCreateView(generics.CreateAPIView):
    """
    Создание новой версии статьи
    """
    serializer_class = ArticleVersionSerializer
    permission_classes = [IsActiveUser, CanEditArticle]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        article_id = self.kwargs['article_id']
        context['original_article'] = get_object_or_404(Article, id=article_id)
        return context


class ArticleStatisticsView(APIView):
    """
    Статистика статей
    """
    permission_classes = [IsModerator]
    
    def get(self, request):
        """
        Возвращает статистику по статьям
        """
        # Общая статистика
        total_articles = Article.objects.active().count()
        published_articles = Article.objects.published().count()
        draft_articles = total_articles - published_articles
        
        # Статистика просмотров
        total_views = ArticleView.objects.count()
        unique_readers = ArticleView.objects.values('user').distinct().count()
        
        # Среднее время чтения
        avg_reading_time = ArticleView.objects.filter(
            reading_time_seconds__isnull=False
        ).aggregate(avg=Avg('reading_time_seconds'))['avg'] or 0
        
        # Популярные категории
        popular_categories = ArticleCategory.objects.filter(
            is_active=True
        ).annotate(
            article_count=Count('articles', filter=Q(articles__is_published=True))
        ).order_by('-article_count')[:5]
        
        category_data = [
            {
                'name': cat.name,
                'count': cat.article_count
            }
            for cat in popular_categories
        ]
        
        # Недавние статьи
        recent_articles = Article.objects.recent(limit=5)
        
        data = {
            'total_articles': total_articles,
            'published_articles': published_articles,
            'draft_articles': draft_articles,
            'total_views': total_views,
            'unique_readers': unique_readers,
            'avg_reading_time': round(avg_reading_time, 2),
            'popular_categories': category_data,
            'recent_articles': ArticleBasicSerializer(recent_articles, many=True).data
        }
        
        return Response(data)


@api_view(['GET'])
@permission_classes([IsActiveUser])
def article_by_category(request, category_slug):
    """
    Статьи по категории
    """
    category = get_object_or_404(ArticleCategory, slug=category_slug, is_active=True)
    articles = Article.objects.by_category(category).select_related('author')
    
    # Пагинация
    from rest_framework.pagination import PageNumberPagination
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(articles, request)
    
    if page is not None:
        serializer = ArticleBasicSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    serializer = ArticleBasicSerializer(articles, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsActiveUser])
def article_by_tag(request, tag):
    """
    Статьи по тегу
    """
    articles = Article.objects.by_tags([tag]).select_related('author', 'category')
    serializer = ArticleBasicSerializer(articles, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsActiveUser])
def toggle_bookmark(request, article_id):
    """
    Добавление/удаление статьи из закладок
    """
    article = get_object_or_404(Article, id=article_id, is_published=True)
    
    bookmark, created = ArticleBookmark.objects.get_or_create(
        article=article,
        user=request.user,
        defaults={'note': request.data.get('note', '')}
    )
    
    if not created:
        bookmark.delete()
        return Response({
            'bookmarked': False,
            'message': 'Статья удалена из закладок'
        })
    
    return Response({
        'bookmarked': True,
        'message': 'Статья добавлена в закладки',
        'bookmark': ArticleBookmarkSerializer(bookmark).data
    })