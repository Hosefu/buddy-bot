# Generated by Django 4.2.16 on 2025-06-14 19:18

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, help_text='Автоматически устанавливается при создании записи', verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, help_text='Автоматически обновляется при изменении записи', verbose_name='Дата обновления')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, help_text='Помечает запись как удаленную без физического удаления', verbose_name='Удалено')),
                ('deleted_at', models.DateTimeField(blank=True, help_text='Время когда запись была помечена как удаленная', null=True, verbose_name='Дата удаления')),
                ('snapshot_created_at', models.DateTimeField(default=django.utils.timezone.now, help_text='Когда был создан этот снапшот', verbose_name='Время создания снапшота')),
                ('content_version', models.CharField(default='1.0', help_text='Версия контента на момент создания снапшота', max_length=50, verbose_name='Версия контента')),
                ('article_title', models.CharField(max_length=255, verbose_name='Название статьи')),
                ('article_content', models.TextField(verbose_name='Содержание статьи')),
                ('article_summary', models.TextField(blank=True, verbose_name='Краткое описание')),
                ('reading_started_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Начало чтения')),
                ('reading_time_seconds', models.PositiveIntegerField(default=0, verbose_name='Время чтения (сек)')),
            ],
            options={
                'verbose_name': 'Снапшот статьи',
                'verbose_name_plural': 'Снапшоты статей',
                'db_table': 'article_snapshots',
            },
        ),
        migrations.CreateModel(
            name='Flow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, help_text='Автоматически устанавливается при создании записи', verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, help_text='Автоматически обновляется при изменении записи', verbose_name='Дата обновления')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, help_text='Помечает запись как удаленную без физического удаления', verbose_name='Удалено')),
                ('deleted_at', models.DateTimeField(blank=True, help_text='Время когда запись была помечена как удаленная', null=True, verbose_name='Дата удаления')),
                ('is_active', models.BooleanField(default=True, help_text='Определяет, активна ли запись в системе', verbose_name='Активно')),
                ('title', models.CharField(help_text='Название потока обучения', max_length=255, verbose_name='Название')),
                ('description', models.TextField(help_text='Подробное описание потока обучения', verbose_name='Описание')),
                ('estimated_duration_hours', models.PositiveIntegerField(blank=True, help_text='Примерное время прохождения в часах', null=True, verbose_name='Ожидаемая продолжительность (часы)')),
                ('is_mandatory', models.BooleanField(default=False, help_text='Обязателен ли поток для всех новых сотрудников', verbose_name='Обязательный')),
                ('auto_assign_departments', models.JSONField(blank=True, default=list, help_text='Список отделов для автоматического назначения потока', verbose_name='Автоназначение отделам')),
            ],
            options={
                'verbose_name': 'Поток обучения',
                'verbose_name_plural': 'Потоки обучения',
                'db_table': 'flows',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='FlowAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, help_text='Автоматически устанавливается при создании записи', verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, help_text='Автоматически обновляется при изменении записи', verbose_name='Дата обновления')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, help_text='Помечает запись как удаленную без физического удаления', verbose_name='Удалено')),
                ('deleted_at', models.DateTimeField(blank=True, help_text='Время когда запись была помечена как удаленная', null=True, verbose_name='Дата удаления')),
                ('action_type', models.CharField(choices=[('started', 'Запущен'), ('paused', 'Приостановлен'), ('resumed', 'Возобновлен'), ('completed', 'Завершен'), ('deleted', 'Удален'), ('extended_deadline', 'Продлен дедлайн'), ('step_completed', 'Этап завершен'), ('quiz_passed', 'Квиз пройден'), ('task_completed', 'Задание выполнено'), ('buddy_assigned', 'Назначен бадди'), ('buddy_removed', 'Удален бадди')], help_text='Тип выполненного действия', max_length=30, verbose_name='Тип действия')),
                ('reason', models.TextField(blank=True, help_text='Причина выполнения действия', null=True, verbose_name='Причина')),
                ('metadata', models.JSONField(blank=True, default=dict, help_text='Дополнительная информация о действии', verbose_name='Метаданные')),
                ('performed_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время выполнения')),
            ],
            options={
                'verbose_name': 'Действие с потоком',
                'verbose_name_plural': 'Действия с потоками',
                'db_table': 'flow_actions',
                'ordering': ['-performed_at'],
            },
        ),
        migrations.CreateModel(
            name='FlowBuddy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, help_text='Автоматически устанавливается при создании записи', verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, help_text='Автоматически обновляется при изменении записи', verbose_name='Дата обновления')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, help_text='Помечает запись как удаленную без физического удаления', verbose_name='Удалено')),
                ('deleted_at', models.DateTimeField(blank=True, help_text='Время когда запись была помечена как удаленная', null=True, verbose_name='Дата удаления')),
                ('can_pause_flow', models.BooleanField(default=True, help_text='Может ли бадди приостанавливать поток', verbose_name='Может приостанавливать')),
                ('can_resume_flow', models.BooleanField(default=True, help_text='Может ли бадди возобновлять поток', verbose_name='Может возобновлять')),
                ('can_extend_deadline', models.BooleanField(default=True, help_text='Может ли бадди продлевать сроки выполнения', verbose_name='Может продлевать дедлайны')),
                ('assigned_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата назначения')),
                ('is_active', models.BooleanField(default=True, help_text='Активен ли бадди для данного потока', verbose_name='Активен')),
            ],
            options={
                'verbose_name': 'Бадди потока',
                'verbose_name_plural': 'Бадди потоков',
                'db_table': 'flow_buddies',
            },
        ),
        migrations.CreateModel(
            name='FlowStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, help_text='Автоматически устанавливается при создании записи', verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, help_text='Автоматически обновляется при изменении записи', verbose_name='Дата обновления')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, help_text='Помечает запись как удаленную без физического удаления', verbose_name='Удалено')),
                ('deleted_at', models.DateTimeField(blank=True, help_text='Время когда запись была помечена как удаленная', null=True, verbose_name='Дата удаления')),
                ('order', models.PositiveIntegerField(default=0, help_text='Порядок отображения элементов', verbose_name='Порядок')),
                ('is_active', models.BooleanField(default=True, help_text='Определяет, активна ли запись в системе', verbose_name='Активно')),
                ('title', models.CharField(help_text='Название этапа потока', max_length=255, verbose_name='Название этапа')),
                ('description', models.TextField(help_text='Описание того, что нужно сделать на этом этапе', verbose_name='Описание')),
                ('step_type', models.CharField(choices=[('article', 'Статья'), ('task', 'Задание'), ('quiz', 'Квиз'), ('mixed', 'Смешанный')], help_text='Тип контента в этапе', max_length=20, verbose_name='Тип этапа')),
                ('is_required', models.BooleanField(default=True, help_text='Обязателен ли этап для завершения потока', verbose_name='Обязательный')),
                ('estimated_time_minutes', models.PositiveIntegerField(blank=True, help_text='Примерное время выполнения этапа', null=True, verbose_name='Ожидаемое время (минуты)')),
            ],
            options={
                'verbose_name': 'Этап потока',
                'verbose_name_plural': 'Этапы потоков',
                'db_table': 'flow_steps',
                'ordering': ['flow', 'order'],
            },
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, help_text='Автоматически устанавливается при создании записи', verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, help_text='Автоматически обновляется при изменении записи', verbose_name='Дата обновления')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, help_text='Помечает запись как удаленную без физического удаления', verbose_name='Удалено')),
                ('deleted_at', models.DateTimeField(blank=True, help_text='Время когда запись была помечена как удаленная', null=True, verbose_name='Дата удаления')),
                ('is_active', models.BooleanField(default=True, help_text='Определяет, активна ли запись в системе', verbose_name='Активно')),
                ('title', models.CharField(help_text='Название квиза', max_length=255, verbose_name='Название квиза')),
                ('description', models.TextField(blank=True, help_text='Описание квиза', null=True, verbose_name='Описание')),
                ('passing_score_percentage', models.PositiveIntegerField(default=70, help_text='Минимальный процент правильных ответов для прохождения', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)], verbose_name='Проходной балл (%)')),
                ('shuffle_questions', models.BooleanField(default=False, help_text='Показывать вопросы в случайном порядке', verbose_name='Перемешивать вопросы')),
                ('shuffle_answers', models.BooleanField(default=False, help_text='Показывать варианты ответов в случайном порядке', verbose_name='Перемешивать ответы')),
            ],
            options={
                'verbose_name': 'Квиз',
                'verbose_name_plural': 'Квизы',
                'db_table': 'quizzes',
            },
        ),
        migrations.CreateModel(
            name='QuizAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, help_text='Автоматически устанавливается при создании записи', verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, help_text='Автоматически обновляется при изменении записи', verbose_name='Дата обновления')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, help_text='Помечает запись как удаленную без физического удаления', verbose_name='Удалено')),
                ('deleted_at', models.DateTimeField(blank=True, help_text='Время когда запись была помечена как удаленная', null=True, verbose_name='Дата удаления')),
                ('order', models.PositiveIntegerField(default=0, help_text='Порядок отображения элементов', verbose_name='Порядок')),
                ('answer_text', models.CharField(help_text='Вариант ответа', max_length=500, verbose_name='Текст ответа')),
                ('is_correct', models.BooleanField(default=False, help_text='Является ли этот ответ правильным', verbose_name='Правильный ответ')),
                ('explanation', models.TextField(help_text='Объяснение почему ответ правильный или неправильный', verbose_name='Объяснение')),
            ],
            options={
                'verbose_name': 'Ответ на вопрос',
                'verbose_name_plural': 'Ответы на вопросы',
                'db_table': 'quiz_answers',
                'ordering': ['question', 'order'],
            },
        ),
        migrations.CreateModel(
            name='QuizAnswerSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, help_text='Автоматически устанавливается при создании записи', verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, help_text='Автоматически обновляется при изменении записи', verbose_name='Дата обновления')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, help_text='Помечает запись как удаленную без физического удаления', verbose_name='Удалено')),
                ('deleted_at', models.DateTimeField(blank=True, help_text='Время когда запись была помечена как удаленная', null=True, verbose_name='Дата удаления')),
                ('snapshot_created_at', models.DateTimeField(default=django.utils.timezone.now, help_text='Когда был создан этот снапшот', verbose_name='Время создания снапшота')),
                ('content_version', models.CharField(default='1.0', help_text='Версия контента на момент создания снапшота', max_length=50, verbose_name='Версия контента')),
                ('original_answer_id', models.PositiveIntegerField(verbose_name='ID оригинального ответа')),
                ('answer_text', models.TextField(verbose_name='Текст ответа')),
                ('is_correct', models.BooleanField(verbose_name='Правильный ответ')),
                ('answer_order', models.PositiveIntegerField(verbose_name='Порядок ответа')),
                ('explanation', models.TextField(blank=True, verbose_name='Объяснение ответа')),
            ],
            options={
                'verbose_name': 'Снапшот ответа',
                'verbose_name_plural': 'Снапшоты ответов',
                'db_table': 'quiz_answer_snapshots',
                'ordering': ['answer_order'],
            },
        ),
        migrations.CreateModel(
            name='QuizQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, help_text='Автоматически устанавливается при создании записи', verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, help_text='Автоматически обновляется при изменении записи', verbose_name='Дата обновления')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, help_text='Помечает запись как удаленную без физического удаления', verbose_name='Удалено')),
                ('deleted_at', models.DateTimeField(blank=True, help_text='Время когда запись была помечена как удаленная', null=True, verbose_name='Дата удаления')),
                ('order', models.PositiveIntegerField(default=0, help_text='Порядок отображения элементов', verbose_name='Порядок')),
                ('question', models.TextField(help_text='Формулировка вопроса', verbose_name='Текст вопроса')),
                ('explanation', models.TextField(blank=True, help_text='Объяснение правильного ответа', null=True, verbose_name='Объяснение')),
            ],
            options={
                'verbose_name': 'Вопрос квиза',
                'verbose_name_plural': 'Вопросы квизов',
                'db_table': 'quiz_questions',
                'ordering': ['quiz', 'order'],
            },
        ),
        migrations.CreateModel(
            name='QuizQuestionSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, help_text='Автоматически устанавливается при создании записи', verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, help_text='Автоматически обновляется при изменении записи', verbose_name='Дата обновления')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, help_text='Помечает запись как удаленную без физического удаления', verbose_name='Удалено')),
                ('deleted_at', models.DateTimeField(blank=True, help_text='Время когда запись была помечена как удаленная', null=True, verbose_name='Дата удаления')),
                ('snapshot_created_at', models.DateTimeField(default=django.utils.timezone.now, help_text='Когда был создан этот снапшот', verbose_name='Время создания снапшота')),
                ('content_version', models.CharField(default='1.0', help_text='Версия контента на момент создания снапшота', max_length=50, verbose_name='Версия контента')),
                ('original_question_id', models.PositiveIntegerField(verbose_name='ID оригинального вопроса')),
                ('question_text', models.TextField(verbose_name='Текст вопроса')),
                ('question_order', models.PositiveIntegerField(verbose_name='Порядок вопроса')),
                ('explanation', models.TextField(blank=True, verbose_name='Объяснение')),
            ],
            options={
                'verbose_name': 'Снапшот вопроса квиза',
                'verbose_name_plural': 'Снапшоты вопросов квизов',
                'db_table': 'quiz_question_snapshots',
                'ordering': ['question_order'],
            },
        ),
        migrations.CreateModel(
            name='QuizSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, help_text='Автоматически устанавливается при создании записи', verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, help_text='Автоматически обновляется при изменении записи', verbose_name='Дата обновления')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, help_text='Помечает запись как удаленную без физического удаления', verbose_name='Удалено')),
                ('deleted_at', models.DateTimeField(blank=True, help_text='Время когда запись была помечена как удаленная', null=True, verbose_name='Дата удаления')),
                ('snapshot_created_at', models.DateTimeField(default=django.utils.timezone.now, help_text='Когда был создан этот снапшот', verbose_name='Время создания снапшота')),
                ('content_version', models.CharField(default='1.0', help_text='Версия контента на момент создания снапшота', max_length=50, verbose_name='Версия контента')),
                ('quiz_title', models.CharField(max_length=255, verbose_name='Название квиза')),
                ('quiz_description', models.TextField(blank=True, verbose_name='Описание квиза')),
                ('passing_score_percentage', models.PositiveIntegerField(verbose_name='Проходной балл (%)')),
                ('total_questions', models.PositiveIntegerField(verbose_name='Всего вопросов')),
                ('correct_answers', models.PositiveIntegerField(verbose_name='Правильных ответов')),
                ('score_percentage', models.PositiveIntegerField(verbose_name='Процент правильных ответов')),
                ('is_passed', models.BooleanField(verbose_name='Квиз пройден')),
            ],
            options={
                'verbose_name': 'Снапшот квиза',
                'verbose_name_plural': 'Снапшоты квизов',
                'db_table': 'quiz_snapshots',
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, help_text='Автоматически устанавливается при создании записи', verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, help_text='Автоматически обновляется при изменении записи', verbose_name='Дата обновления')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, help_text='Помечает запись как удаленную без физического удаления', verbose_name='Удалено')),
                ('deleted_at', models.DateTimeField(blank=True, help_text='Время когда запись была помечена как удаленная', null=True, verbose_name='Дата удаления')),
                ('title', models.CharField(help_text='Название задания', max_length=255, verbose_name='Название задания')),
                ('description', models.TextField(help_text='Подробное описание того, что нужно сделать', verbose_name='Описание задания')),
                ('instruction', models.TextField(help_text='Инструкция где искать кодовое слово', verbose_name='Инструкция')),
                ('code_word', models.CharField(help_text='Правильное кодовое слово', max_length=100, verbose_name='Кодовое слово')),
                ('hint', models.TextField(blank=True, help_text='Подсказка для выполнения задания', null=True, verbose_name='Подсказка')),
            ],
            options={
                'verbose_name': 'Задание',
                'verbose_name_plural': 'Задания',
                'db_table': 'tasks',
            },
        ),
        migrations.CreateModel(
            name='TaskSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, help_text='Автоматически устанавливается при создании записи', verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, help_text='Автоматически обновляется при изменении записи', verbose_name='Дата обновления')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, help_text='Помечает запись как удаленную без физического удаления', verbose_name='Удалено')),
                ('deleted_at', models.DateTimeField(blank=True, help_text='Время когда запись была помечена как удаленная', null=True, verbose_name='Дата удаления')),
                ('snapshot_created_at', models.DateTimeField(default=django.utils.timezone.now, help_text='Когда был создан этот снапшот', verbose_name='Время создания снапшота')),
                ('content_version', models.CharField(default='1.0', help_text='Версия контента на момент создания снапшота', max_length=50, verbose_name='Версия контента')),
                ('task_title', models.CharField(max_length=255, verbose_name='Название задания')),
                ('task_description', models.TextField(verbose_name='Описание задания')),
                ('task_instruction', models.TextField(blank=True, null=True, verbose_name='Инструкция')),
                ('task_code_word', models.CharField(max_length=100, verbose_name='Кодовое слово')),
                ('task_hint', models.TextField(blank=True, null=True, verbose_name='Подсказка')),
                ('user_answer', models.CharField(max_length=255, verbose_name='Ответ пользователя')),
                ('is_correct', models.BooleanField(verbose_name='Правильный ответ')),
                ('attempts_count', models.PositiveIntegerField(default=1, verbose_name='Количество попыток')),
            ],
            options={
                'verbose_name': 'Снапшот задания',
                'verbose_name_plural': 'Снапшоты заданий',
                'db_table': 'task_snapshots',
            },
        ),
        migrations.CreateModel(
            name='UserFlow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, help_text='Автоматически устанавливается при создании записи', verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, help_text='Автоматически обновляется при изменении записи', verbose_name='Дата обновления')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, help_text='Помечает запись как удаленную без физического удаления', verbose_name='Удалено')),
                ('deleted_at', models.DateTimeField(blank=True, help_text='Время когда запись была помечена как удаленная', null=True, verbose_name='Дата удаления')),
                ('status', models.CharField(choices=[('not_started', 'Не начат'), ('in_progress', 'В процессе'), ('paused', 'Приостановлен'), ('completed', 'Завершен'), ('suspended', 'Заблокировано')], default='not_started', help_text='Текущий статус прохождения потока', max_length=20, verbose_name='Статус')),
                ('paused_at', models.DateTimeField(blank=True, null=True, verbose_name='Время приостановки')),
                ('pause_reason', models.TextField(blank=True, null=True, verbose_name='Причина приостановки')),
                ('expected_completion_date', models.DateField(blank=True, help_text='Дедлайн для завершения потока', null=True, verbose_name='Ожидаемая дата завершения')),
                ('started_at', models.DateTimeField(blank=True, null=True, verbose_name='Время начала')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Время завершения')),
                ('current_step', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='current_user_flows', to='flows.flowstep', verbose_name='Текущий этап')),
                ('flow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_flows', to='flows.flow', verbose_name='Поток')),
            ],
            options={
                'verbose_name': 'Прохождение потока',
                'verbose_name_plural': 'Прохождения потоков',
                'db_table': 'user_flows',
            },
        ),
        migrations.CreateModel(
            name='UserStepProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, help_text='Автоматически устанавливается при создании записи', verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, help_text='Автоматически обновляется при изменении записи', verbose_name='Дата обновления')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, help_text='Помечает запись как удаленную без физического удаления', verbose_name='Удалено')),
                ('deleted_at', models.DateTimeField(blank=True, help_text='Время когда запись была помечена как удаленная', null=True, verbose_name='Дата удаления')),
                ('status', models.CharField(choices=[('locked', 'Заблокирован'), ('available', 'Доступен'), ('in_progress', 'В процессе'), ('completed', 'Завершен')], default='locked', help_text='Статус прохождения этапа', max_length=20, verbose_name='Статус')),
                ('article_read_at', models.DateTimeField(blank=True, null=True, verbose_name='Статья прочитана')),
                ('task_completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Задание выполнено')),
                ('quiz_completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Квиз завершен')),
                ('quiz_correct_answers', models.PositiveIntegerField(blank=True, null=True, verbose_name='Правильных ответов в квизе')),
                ('quiz_total_questions', models.PositiveIntegerField(blank=True, null=True, verbose_name='Всего вопросов в квизе')),
                ('started_at', models.DateTimeField(blank=True, null=True, verbose_name='Время начала')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Время завершения')),
                ('flow_step', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_progress', to='flows.flowstep', verbose_name='Этап потока')),
                ('user_flow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='step_progress', to='flows.userflow', verbose_name='Прохождение потока')),
            ],
            options={
                'verbose_name': 'Прогресс по этапу',
                'verbose_name_plural': 'Прогресс по этапам',
                'db_table': 'user_step_progress',
            },
        ),
        migrations.CreateModel(
            name='UserQuizAnswerSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, help_text='Автоматически устанавливается при создании записи', verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, help_text='Автоматически обновляется при изменении записи', verbose_name='Дата обновления')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, help_text='Помечает запись как удаленную без физического удаления', verbose_name='Удалено')),
                ('deleted_at', models.DateTimeField(blank=True, help_text='Время когда запись была помечена как удаленная', null=True, verbose_name='Дата удаления')),
                ('snapshot_created_at', models.DateTimeField(default=django.utils.timezone.now, help_text='Когда был создан этот снапшот', verbose_name='Время создания снапшота')),
                ('content_version', models.CharField(default='1.0', help_text='Версия контента на момент создания снапшота', max_length=50, verbose_name='Версия контента')),
                ('is_correct', models.BooleanField(verbose_name='Ответ правильный')),
                ('answered_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время ответа')),
                ('question_snapshot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_answer', to='flows.quizquestionsnapshot', verbose_name='Снапшот вопроса')),
                ('quiz_snapshot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_answers', to='flows.quizsnapshot', verbose_name='Снапшот квиза')),
                ('selected_answer_snapshot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_selections', to='flows.quizanswersnapshot', verbose_name='Выбранный ответ (снапшот)')),
            ],
            options={
                'verbose_name': 'Ответ пользователя (снапшот)',
                'verbose_name_plural': 'Ответы пользователей (снапшоты)',
                'db_table': 'user_quiz_answer_snapshots',
            },
        ),
        migrations.CreateModel(
            name='UserQuizAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, help_text='Автоматически устанавливается при создании записи', verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, help_text='Автоматически обновляется при изменении записи', verbose_name='Дата обновления')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, help_text='Помечает запись как удаленную без физического удаления', verbose_name='Удалено')),
                ('deleted_at', models.DateTimeField(blank=True, help_text='Время когда запись была помечена как удаленная', null=True, verbose_name='Дата удаления')),
                ('is_correct', models.BooleanField(help_text='Был ли ответ правильным', verbose_name='Правильный ответ')),
                ('answered_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время ответа')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_answers', to='flows.quizquestion', verbose_name='Вопрос')),
                ('selected_answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_selections', to='flows.quizanswer', verbose_name='Выбранный ответ')),
                ('user_flow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quiz_answers', to='flows.userflow', verbose_name='Прохождение потока')),
            ],
            options={
                'verbose_name': 'Ответ пользователя на квиз',
                'verbose_name_plural': 'Ответы пользователей на квизы',
                'db_table': 'user_quiz_answers',
            },
        ),
    ]
