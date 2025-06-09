"""
URL конфигурация для статей и гайдов
"""
from django.urls import path
from .views import (
    # Категории
    ArticleCategoryListView, ArticleCategoryTreeView, ArticleCategoryDetailView,
    
    # Статьи
    ArticleListView, ArticleDetailView, ArticleSearchView,
    PopularArticlesView, RecentArticlesView, RelatedArticlesView,
    
    # Закладки
    ArticleBookmarkListView, ArticleBookmarkDetailView,
    
    # Административные
    AdminArticleListView, AdminArticleReviewListView, AdminArticleReviewDetailView,
    PublishArticleView, ArticleVersionCreateView, ArticleStatisticsView,
    
    # Функциональные эндпоинты
    article_by_category, article_by_tag, toggle_bookmark
)

app_name = 'guides'

urlpatterns = [
    # Категории статей
    path('categories/', ArticleCategoryListView.as_view(), name='category-list'),
    path('categories/tree/', ArticleCategoryTreeView.as_view(), name='category-tree'),
    path('categories/<slug:slug>/', ArticleCategoryDetailView.as_view(), name='category-detail'),
    
    # Статьи
    path('', ArticleListView.as_view(), name='article-list'),
    path('search/', ArticleSearchView.as_view(), name='article-search'),
    path('popular/', PopularArticlesView.as_view(), name='popular-articles'),
    path('recent/', RecentArticlesView.as_view(), name='recent-articles'),
    path('<slug:slug>/', ArticleDetailView.as_view(), name='article-detail'),
    path('<slug:slug>/related/', RelatedArticlesView.as_view(), name='related-articles'),
    
    # Закладки
    path('bookmarks/', ArticleBookmarkListView.as_view(), name='bookmark-list'),
    path('bookmarks/<int:pk>/', ArticleBookmarkDetailView.as_view(), name='bookmark-detail'),
    path('<int:article_id>/toggle-bookmark/', toggle_bookmark, name='toggle-bookmark'),
    
    # Фильтрация
    path('category/<slug:category_slug>/', article_by_category, name='articles-by-category'),
    path('tag/<str:tag>/', article_by_tag, name='articles-by-tag'),
    
    # Административные функции
    path('admin/articles/', AdminArticleListView.as_view(), name='admin-article-list'),
    path('admin/articles/<int:article_id>/reviews/', AdminArticleReviewListView.as_view(), name='admin-article-reviews'),
    path('admin/reviews/<int:pk>/', AdminArticleReviewDetailView.as_view(), name='admin-review-detail'),
    path('admin/articles/<int:article_id>/publish/', PublishArticleView.as_view(), name='publish-article'),
    path('admin/articles/<int:article_id>/versions/', ArticleVersionCreateView.as_view(), name='article-version-create'),
    path('admin/statistics/', ArticleStatisticsView.as_view(), name='article-statistics'),
]