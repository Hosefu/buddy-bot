"""
Административная панель для потоков обучения
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count

from .models import (
    Flow, FlowStep, Task, Quiz, QuizQuestion, QuizAnswer,
    UserFlow, FlowBuddy, UserStepProgress, UserQuizAnswer, FlowAction
)


class FlowStepInline(admin.TabularInline):
    """
    Инлайн для этапов потока
    """
    model = FlowStep
    extra = 0
    fields = ['title', 'step_type', 'order', 'is_required', 'is_active']
    readonly_fields = ['created_at']
    ordering = ['order']


@admin.register(Flow)
class FlowAdmin(admin.ModelAdmin):
    """
    Административная панель для потоков обучения
    """
    list_display = [
        'title', 'total_steps_display', 'required_steps_display',
        'is_mandatory', 'is_active', 'assignments_count', 'created_at'
    ]
    list_filter = ['is_mandatory', 'is_active', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'total_steps', 'required_steps']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'estimated_duration_hours')
        }),
        ('Настройки', {
            'fields': ('is_mandatory', 'auto_assign_departments', 'is_active')
        }),
        ('Статистика', {
            'fields': ('total_steps', 'required_steps'),
            'classes': ('collapse',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [FlowStepInline]
    
    def total_steps_display(self, obj):
        return obj.total_steps
    total_steps_display.short_description = 'Всего этапов'
    
    def required_steps_display(self, obj):
        return obj.required_steps
    required_steps_display.short_description = 'Обязательных'
    
    def assignments_count(self, obj):
        """Количество назначений потока"""
        count = obj.user_flows.count()
        if count > 0:
            url = reverse('admin:flows_userflow_changelist') + f'?flow__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return 0
    assignments_count.short_description = 'Назначений'
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            assignments_count=Count('user_flows')
        )


class TaskInline(admin.StackedInline):
    """
    Инлайн для заданий
    """
    model = Task
    extra = 0
    fields = ['title', 'description', 'instruction', 'code_word', 'hint']


class QuizInline(admin.StackedInline):
    """
    Инлайн для квизов
    """
    model = Quiz
    extra = 0
    fields = ['title', 'description', 'passing_score_percentage', 'shuffle_questions', 'shuffle_answers']


@admin.register(FlowStep)
class FlowStepAdmin(admin.ModelAdmin):
    """
    Административная панель для этапов потоков
    """
    list_display = [
        'title', 'flow_title', 'step_type', 'order', 
        'is_required', 'is_active', 'estimated_time_minutes'
    ]
    list_filter = ['step_type', 'is_required', 'is_active', 'flow']
    search_fields = ['title', 'description', 'flow__title']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('flow', 'title', 'description', 'step_type', 'order')
        }),
        ('Настройки', {
            'fields': ('is_required', 'estimated_time_minutes', 'is_active')
        }),
        ('Контент', {
            'fields': ('article',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [TaskInline, QuizInline]
    
    def flow_title(self, obj):
        return obj.flow.title
    flow_title.short_description = 'Поток'
    flow_title.admin_order_field = 'flow__title'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('flow')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Административная панель для заданий
    """
    list_display = ['title', 'flow_step_title', 'code_word', 'created_at']
    list_filter = ['flow_step__flow', 'created_at']
    search_fields = ['title', 'description', 'flow_step__title']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('flow_step', 'title', 'description')
        }),
        ('Задание', {
            'fields': ('instruction', 'code_word', 'hint')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def flow_step_title(self, obj):
        return f"{obj.flow_step.flow.title} - {obj.flow_step.title}"
    flow_step_title.short_description = 'Этап'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('flow_step__flow')


class QuizAnswerInline(admin.TabularInline):
    """
    Инлайн для ответов на вопросы квиза
    """
    model = QuizAnswer
    extra = 2
    fields = ['answer_text', 'is_correct', 'explanation', 'order']
    ordering = ['order']


class QuizQuestionInline(admin.StackedInline):
    """
    Инлайн для вопросов квиза
    """
    model = QuizQuestion
    extra = 0
    fields = ['question', 'explanation', 'order']
    ordering = ['order']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """
    Административная панель для квизов
    """
    list_display = [
        'title', 'flow_step_title', 'total_questions', 
        'passing_score_percentage', 'is_active'
    ]
    list_filter = ['flow_step__flow', 'passing_score_percentage', 'is_active']
    search_fields = ['title', 'description', 'flow_step__title']
    readonly_fields = ['created_at', 'updated_at', 'total_questions']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('flow_step', 'title', 'description')
        }),
        ('Настройки квиза', {
            'fields': ('passing_score_percentage', 'shuffle_questions', 'shuffle_answers', 'is_active')
        }),
        ('Статистика', {
            'fields': ('total_questions',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [QuizQuestionInline]
    
    def flow_step_title(self, obj):
        return f"{obj.flow_step.flow.title} - {obj.flow_step.title}"
    flow_step_title.short_description = 'Этап'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('flow_step__flow')


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    """
    Административная панель для вопросов квизов
    """
    list_display = ['question_preview', 'quiz_title', 'order', 'answers_count']
    list_filter = ['quiz__flow_step__flow', 'quiz']
    search_fields = ['question', 'quiz__title']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Вопрос', {
            'fields': ('quiz', 'question', 'explanation', 'order')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [QuizAnswerInline]
    
    def question_preview(self, obj):
        return obj.question[:100] + '...' if len(obj.question) > 100 else obj.question
    question_preview.short_description = 'Вопрос'
    
    def quiz_title(self, obj):
        return obj.quiz.title
    quiz_title.short_description = 'Квиз'
    
    def answers_count(self, obj):
        return obj.answers.count()
    answers_count.short_description = 'Ответов'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('quiz').annotate(
            answers_count=Count('answers')
        )


class FlowBuddyInline(admin.TabularInline):
    """
    Инлайн для бадди потока
    """
    model = FlowBuddy
    extra = 0
    fields = ['buddy_user', 'can_pause_flow', 'can_resume_flow', 'can_extend_deadline', 'is_active']
    readonly_fields = ['assigned_at']


class UserStepProgressInline(admin.TabularInline):
    """
    Инлайн для прогресса по этапам
    """
    model = UserStepProgress
    extra = 0
    fields = ['flow_step', 'status', 'completed_at']
    readonly_fields = ['flow_step', 'created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('flow_step').order_by('flow_step__order')


@admin.register(UserFlow)
class UserFlowAdmin(admin.ModelAdmin):
    """
    Административная панель для прохождения потоков
    """
    list_display = [
        'user_name', 'flow_title', 'status', 'progress_display',
        'is_overdue_display', 'started_at', 'expected_completion_date'
    ]
    list_filter = ['status', 'flow', 'expected_completion_date', 'started_at']
    search_fields = ['user__name', 'user__email', 'flow__title']
    readonly_fields = [
        'created_at', 'updated_at', 'progress_percentage', 'is_overdue'
    ]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'flow', 'status', 'current_step')
        }),
        ('Управление', {
            'fields': ('paused_by', 'paused_at', 'pause_reason', 'expected_completion_date')
        }),
        ('Прогресс', {
            'fields': ('progress_percentage', 'is_overdue', 'started_at', 'completed_at')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [FlowBuddyInline, UserStepProgressInline]
    
    def user_name(self, obj):
        return obj.user.name
    user_name.short_description = 'Пользователь'
    user_name.admin_order_field = 'user__name'
    
    def flow_title(self, obj):
        return obj.flow.title
    flow_title.short_description = 'Поток'
    flow_title.admin_order_field = 'flow__title'
    
    def progress_display(self, obj):
        progress = obj.progress_percentage
        if progress >= 100:
            color = 'green'
        elif progress >= 50:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, progress
        )
    progress_display.short_description = 'Прогресс'
    
    def is_overdue_display(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color: red;">Просрочено</span>')
        return '-'
    is_overdue_display.short_description = 'Просрочка'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'flow', 'current_step')


@admin.register(FlowAction)
class FlowActionAdmin(admin.ModelAdmin):
    """
    Административная панель для действий с потоками
    """
    list_display = [
        'action_type', 'user_flow_display', 'performed_by_name', 
        'performed_at', 'reason_preview'
    ]
    list_filter = ['action_type', 'performed_at', 'user_flow__flow']
    search_fields = ['user_flow__user__name', 'performed_by__name', 'reason']
    readonly_fields = ['performed_at', 'created_at']
    
    fieldsets = (
        ('Действие', {
            'fields': ('user_flow', 'action_type', 'performed_by', 'performed_at')
        }),
        ('Детали', {
            'fields': ('reason', 'metadata')
        }),
        ('Служебная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def user_flow_display(self, obj):
        return f"{obj.user_flow.user.name} - {obj.user_flow.flow.title}"
    user_flow_display.short_description = 'Прохождение'
    
    def performed_by_name(self, obj):
        return obj.performed_by.name
    performed_by_name.short_description = 'Выполнил'
    performed_by_name.admin_order_field = 'performed_by__name'
    
    def reason_preview(self, obj):
        if obj.reason:
            return obj.reason[:100] + '...' if len(obj.reason) > 100 else obj.reason
        return '-'
    reason_preview.short_description = 'Причина'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user_flow__user', 'user_flow__flow', 'performed_by'
        )
    
    def has_add_permission(self, request):
        """Запрещаем ручное создание действий"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Запрещаем редактирование действий"""
        return False