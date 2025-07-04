# Generated by Django 4.2.16 on 2025-06-14 19:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('guides', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='articleview',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='article_views', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddField(
            model_name='articlereview',
            name='article',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='guides.article', verbose_name='Статья'),
        ),
        migrations.AddField(
            model_name='articlereview',
            name='reviewer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='article_reviews', to=settings.AUTH_USER_MODEL, verbose_name='Рецензент'),
        ),
        migrations.AddField(
            model_name='articlecategory',
            name='parent',
            field=models.ForeignKey(blank=True, help_text='Родительская категория для создания иерархии', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='guides.articlecategory', verbose_name='Родительская категория'),
        ),
        migrations.AddField(
            model_name='articlebookmark',
            name='article',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookmarks', to='guides.article', verbose_name='Статья'),
        ),
        migrations.AddField(
            model_name='articlebookmark',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookmarked_articles', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddField(
            model_name='article',
            name='author',
            field=models.ForeignKey(blank=True, help_text='Автор статьи', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='authored_articles', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AddField(
            model_name='article',
            name='category',
            field=models.ForeignKey(blank=True, help_text='Категория статьи', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='articles', to='guides.articlecategory', verbose_name='Категория'),
        ),
        migrations.AddField(
            model_name='article',
            name='previous_version',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='newer_versions', to='guides.article', verbose_name='Предыдущая версия'),
        ),
        migrations.AddField(
            model_name='article',
            name='reviewers',
            field=models.ManyToManyField(blank=True, related_name='reviewed_articles', through='guides.ArticleReview', to=settings.AUTH_USER_MODEL, verbose_name='Рецензенты'),
        ),
        migrations.AddIndex(
            model_name='articleview',
            index=models.Index(fields=['article', 'user'], name='article_vie_article_37b07a_idx'),
        ),
        migrations.AddIndex(
            model_name='articleview',
            index=models.Index(fields=['user', 'viewed_at'], name='article_vie_user_id_471fed_idx'),
        ),
        migrations.AddIndex(
            model_name='articleview',
            index=models.Index(fields=['flow_step', 'viewed_at'], name='article_vie_flow_st_3d000f_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='articlereview',
            unique_together={('article', 'reviewer')},
        ),
        migrations.AlterUniqueTogether(
            name='articlebookmark',
            unique_together={('article', 'user')},
        ),
        migrations.AddIndex(
            model_name='article',
            index=models.Index(fields=['is_published', 'is_active'], name='articles_is_publ_5ad717_idx'),
        ),
        migrations.AddIndex(
            model_name='article',
            index=models.Index(fields=['category', 'is_published'], name='articles_categor_9d3809_idx'),
        ),
        migrations.AddIndex(
            model_name='article',
            index=models.Index(fields=['article_type', 'is_published'], name='articles_article_a3deec_idx'),
        ),
        migrations.AddIndex(
            model_name='article',
            index=models.Index(fields=['author', 'is_published'], name='articles_author__63b90f_idx'),
        ),
    ]
