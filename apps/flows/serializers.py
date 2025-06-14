"""
Сериализаторы для системы потоков обучения
"""
from rest_framework import serializers
from django.utils import timezone
from django.db import transaction
from django.db import models
import random

from .models import (
    Flow, FlowStep, Task, Quiz, QuizQuestion, QuizAnswer,
    UserFlow, FlowBuddy, UserStepProgress, UserQuizAnswer, FlowAction
)
from .snapshot_models import (
    TaskSnapshot, QuizSnapshot, QuizQuestionSnapshot,
    QuizAnswerSnapshot, UserQuizAnswerSnapshot
)
from apps.users.serializers import UserListSerializer
from apps.guides.serializers import ArticleBasicSerializer


class FlowBasicSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор потока обучения
    """
    total_steps = serializers.ReadOnlyField()
    required_steps = serializers.ReadOnlyField()
    
    class Meta:
        model = Flow
        fields = [
            'id', 'title', 'description', 'estimated_duration_hours',
            'is_mandatory', 'is_active', 'total_steps', 'required_steps',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FlowSerializer(FlowBasicSerializer):
    """
    Полный сериализатор потока обучения
    """
    auto_assign_departments = serializers.ListField(
        child=serializers.CharField(max_length=255),
        required=False,
        allow_empty=True
    )
    
    class Meta(FlowBasicSerializer.Meta):
        fields = FlowBasicSerializer.Meta.fields + ['auto_assign_departments']


class TaskSerializer(serializers.ModelSerializer):
    """
    Сериализатор задания
    """
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'instruction', 
            'hint', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """Скрываем кодовое слово от пользователей"""
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        # Показываем кодовое слово только модераторам
        if request and request.user.has_role('moderator'):
            data['code_word'] = instance.code_word
        
        return data


class TaskAnswerSerializer(serializers.Serializer):
    """
    Сериализатор для ответа на задание
    """
    answer = serializers.CharField(max_length=100)
    
    def validate_answer(self, value):
        """Валидация ответа"""
        if not value.strip():
            raise serializers.ValidationError("Ответ не может быть пустым")
        return value.strip()


class QuizAnswerSerializer(serializers.ModelSerializer):
    """
    Сериализатор варианта ответа на вопрос квиза
    """
    class Meta:
        model = QuizAnswer
        fields = [
            'id', 'answer_text', 'order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """Скрываем правильность ответа и объяснения до выбора"""
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        # Показываем правильность и объяснения только модераторам
        # или после ответа пользователя
        if request and (
            request.user.has_role('moderator') or 
            self.context.get('show_correct_answers', False)
        ):
            data['is_correct'] = instance.is_correct
            data['explanation'] = instance.explanation
        
        return data


class QuizQuestionSerializer(serializers.ModelSerializer):
    """
    Сериализатор вопроса квиза
    """
    answers = QuizAnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizQuestion
        fields = [
            'id', 'question', 'order', 'answers', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """Скрываем объяснения от пользователей до ответа"""
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        # Показываем объяснения только модераторам
        if request and request.user.has_role('moderator'):
            data['explanation'] = instance.explanation
        
        return data


class QuizSerializer(serializers.ModelSerializer):
    """
    Сериализатор квиза
    """
    questions = QuizQuestionSerializer(many=True, read_only=True)
    total_questions = serializers.ReadOnlyField()
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'passing_score_percentage',
            'shuffle_questions', 'shuffle_answers', 'total_questions',
            'questions', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        questions = data.get('questions', [])
        
        if instance.shuffle_questions:
            random.shuffle(questions)
            
        if instance.shuffle_answers:
            for question in questions:
                if 'answers' in question:
                    random.shuffle(question['answers'])
                    
        data['questions'] = questions
        return data


class FlowStepSerializer(serializers.ModelSerializer):
    """
    Сериализатор этапа потока
    """
    article = ArticleBasicSerializer(read_only=True)
    task = TaskSerializer(read_only=True)
    quiz = QuizSerializer(read_only=True)
    
    class Meta:
        model = FlowStep
        fields = [
            'id', 'title', 'description', 'step_type', 'order',
            'is_required', 'estimated_time_minutes', 'is_active',
            'article', 'task', 'quiz', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FlowDetailSerializer(FlowSerializer):
    """
    Подробный сериализатор потока с этапами
    """
    flow_steps = FlowStepSerializer(many=True, read_only=True)
    
    class Meta(FlowSerializer.Meta):
        fields = FlowSerializer.Meta.fields + ['flow_steps']


class QuizAnswerSnapshotSerializer(serializers.ModelSerializer):
    """Сериализатор снапшота ответа"""
    
    class Meta:
        model = QuizAnswerSnapshot
        fields = [
            'id', 'answer_text', 'is_correct', 'answer_order', 'explanation'
        ]


class UserQuizAnswerSnapshotSerializer(serializers.ModelSerializer):
    """Сериализатор ответа пользователя (снапшот)"""
    selected_answer = QuizAnswerSnapshotSerializer(source='selected_answer_snapshot', read_only=True)
    
    class Meta:
        model = UserQuizAnswerSnapshot
        fields = [
            'id', 'selected_answer', 'is_correct', 'answered_at'
        ]


class QuizQuestionSnapshotSerializer(serializers.ModelSerializer):
    """Сериализатор снапшота вопроса квиза"""
    answer_options = QuizAnswerSnapshotSerializer(many=True, read_only=True)
    user_answers = UserQuizAnswerSnapshotSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizQuestionSnapshot
        fields = [
            'id', 'question_text', 'question_order', 'explanation',
            'answer_options', 'user_answers'
        ]


class QuizSnapshotSerializer(serializers.ModelSerializer):
    """Сериализатор снапшота квиза"""
    questions = QuizQuestionSnapshotSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizSnapshot
        fields = [
            'id', 'quiz_title', 'quiz_description', 'passing_score_percentage',
            'total_questions', 'correct_answers', 'score_percentage', 'is_passed',
            'questions', 'created_at'
        ]


class TaskSnapshotSerializer(serializers.ModelSerializer):
    """Сериализатор снапшота задания"""
    
    class Meta:
        model = TaskSnapshot
        fields = [
            'id', 'task_title', 'task_description', 'task_instruction',
            'task_hint', 'user_answer', 'is_correct', 'attempts_count',
            'created_at'
        ]


class UserStepProgressSerializer(serializers.ModelSerializer):
    """
    Сериализатор прогресса по этапу
    """
    flow_step = FlowStepSerializer(read_only=True)
    is_accessible = serializers.ReadOnlyField()
    quiz_score_percentage = serializers.ReadOnlyField()
    task_snapshot = TaskSnapshotSerializer(read_only=True)
    quiz_snapshot = QuizSnapshotSerializer(read_only=True)
    
    class Meta:
        model = UserStepProgress
        fields = [
            'id', 'flow_step', 'status', 'is_accessible',
            'article_read_at', 'task_completed_at', 'quiz_completed_at',
            'quiz_correct_answers', 'quiz_total_questions', 
            'quiz_score_percentage', 'started_at', 'completed_at',
            'task_snapshot', 'quiz_snapshot',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'article_read_at', 'task_completed_at', 'quiz_completed_at',
            'started_at', 'completed_at', 'created_at', 'updated_at'
        ]


class FlowBuddySerializer(serializers.ModelSerializer):
    """
    Сериализатор бадди потока
    """
    buddy_user = UserListSerializer(read_only=True)
    assigned_by_name = serializers.CharField(
        source='assigned_by.name', 
        read_only=True
    )
    
    class Meta:
        model = FlowBuddy
        fields = [
            'id', 'buddy_user', 'can_pause_flow', 'can_resume_flow',
            'can_extend_deadline', 'assigned_by_name', 'assigned_at',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'assigned_at', 'created_at']


class UserFlowSerializer(serializers.ModelSerializer):
    """
    Сериализатор прохождения потока пользователем
    """
    flow = FlowBasicSerializer(read_only=True)
    user = UserListSerializer(read_only=True)
    current_step = FlowStepSerializer(read_only=True)
    flow_buddies = FlowBuddySerializer(many=True, read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    paused_by_name = serializers.CharField(
        source='paused_by.name', 
        read_only=True
    )
    
    class Meta:
        model = UserFlow
        fields = [
            'id', 'user', 'flow', 'status', 'current_step',
            'progress_percentage', 'is_overdue', 'flow_buddies',
            'paused_by_name', 'paused_at', 'pause_reason',
            'expected_completion_date', 'started_at', 'completed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'paused_by_name', 'paused_at', 'started_at', 
            'completed_at', 'created_at', 'updated_at'
        ]


class UserFlowDetailSerializer(UserFlowSerializer):
    """
    Подробный сериализатор прохождения потока с прогрессом по этапам
    """
    step_progress = serializers.SerializerMethodField()
    
    class Meta(UserFlowSerializer.Meta):
        fields = UserFlowSerializer.Meta.fields + ['step_progress']
    
    def get_step_progress(self, obj):
        """
        Возвращает прогресс по этапам с учетом прав пользователя
        """
        request = self.context.get('request')
        if not request:
            return []
        
        user = request.user
        
        # Для модераторов и бадди - показываем все этапы
        if user.has_role('moderator') or (
            user.has_role('buddy') and 
            obj.flow_buddies.filter(buddy_user=user, is_active=True).exists()
        ):
            step_progress = obj.step_progress.all().order_by('flow_step__order')
            return UserStepProgressSerializer(step_progress, many=True, context=self.context).data
        
        # Для обычного пользователя - только доступные и завершенные этапы
        if user == obj.user:
            step_progress = obj.step_progress.filter(
                models.Q(status__in=['completed', 'in_progress']) |
                models.Q(flow_step__order=obj.current_step.order if obj.current_step else 1)
            ).order_by('flow_step__order')
            
            serialized_steps = []
            for progress in step_progress:
                step_data = UserStepProgressSerializer(progress, context=self.context).data
                
                # Для будущих этапов показываем только заголовок
                if progress.status == 'locked':
                    step_data = {
                        'id': step_data['id'],
                        'flow_step_title': step_data.get('flow_step_title'),
                        'status': 'locked',
                        'order': step_data.get('order')
                    }
                
                serialized_steps.append(step_data)
            
            return serialized_steps
        
        # Для остальных - доступ запрещен
        return []


class UserFlowStartSerializer(serializers.Serializer):
    """
    Сериализатор для запуска потока пользователем
    """
    user_id = serializers.IntegerField()
    expected_completion_date = serializers.DateField(required=False)
    additional_buddies = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    
    def validate_user_id(self, value):
        """Валидация пользователя"""
        from apps.users.models import User
        try:
            user = User.objects.get(id=value, is_active=True)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден")
    
    def validate_additional_buddies(self, value):
        """Валидация дополнительных бадди"""
        from apps.users.models import User
        if not value:
            return []
        
        buddies = User.objects.filter(
            id__in=value,
            is_active=True,
            user_roles__role__name='buddy',
            user_roles__is_active=True
        )
        
        if len(buddies) != len(value):
            raise serializers.ValidationError("Некоторые пользователи не найдены или не являются бадди")
        
        return list(buddies)
    
    def validate(self, data):
        """Проверяет, что для данной пары user-flow еще нет активного UserFlow."""
        user_id = data.get('user_id')
        flow = self.context['flow']
        # Убираем проверку отсюда, чтобы view мог вернуть 409 вместо 400
        # if UserFlow.objects.filter(user_id=user_id, flow=flow, status__in=['in_progress', 'paused']).exists():
        #     raise serializers.ValidationError(
        #         "Для этого пользователя уже запущен этот поток.",
        #         code='conflict'
        #     )
        return data

    @transaction.atomic
    def create(self, validated_data):
        """Создает UserFlow и назначает бадди."""
        user = validated_data['user_id']
        flow = self.context['flow']
        assigner = self.context['request'].user
        additional_buddies = validated_data.get('additional_buddies', [])

        # Если срок выполнения не указан, рассчитываем его автоматически
        expected_completion_date = validated_data.get('expected_completion_date')
        if not expected_completion_date:
            expected_completion_date = flow.calculate_expected_completion_date()

        # Создаем UserFlow сразу со статусом IN_PROGRESS
        user_flow = UserFlow.objects.create(
            user=user,
            flow=flow,
            expected_completion_date=expected_completion_date,
            status=UserFlow.FlowStatus.IN_PROGRESS
        )

        # Создатель запроса автоматически становится бадди
        buddies_to_create = {assigner}
        buddies_to_create.update(additional_buddies)

        for buddy in buddies_to_create:
            FlowBuddy.objects.create(
                user_flow=user_flow,
                buddy_user=buddy,
                assigned_by=assigner
            )
        
        # Записываем действие в историю (сигнал это делает, но тут подробнее)
        FlowAction.objects.create(
            user_flow=user_flow,
            action_type=FlowAction.ActionType.STARTED,
            performed_by=assigner,
            reason="Поток назначен бадди",
            metadata={
                'user_id': user.id,
                'user_name': user.name,
                'buddies': [b.id for b in buddies_to_create]
            }
        )
        return user_flow


class FlowActionSerializer(serializers.ModelSerializer):
    """
    Сериализатор действий с потоком
    """
    performed_by = UserListSerializer(read_only=True)
    action_type_display = serializers.CharField(
        source='get_action_type_display',
        read_only=True
    )
    
    class Meta:
        model = FlowAction
        fields = [
            'id', 'action_type', 'action_type_display', 'performed_by',
            'reason', 'metadata', 'performed_at'
        ]
        read_only_fields = ['id', 'performed_at']


class FlowPauseSerializer(serializers.Serializer):
    """
    Сериализатор для приостановки потока
    """
    reason = serializers.CharField(required=False, allow_blank=True)
    
    def save(self, user_flow, user):
        """Приостановка потока"""
        user_flow.pause(
            paused_by=user,
            reason=self.validated_data.get('reason')
        )
        
        # Записываем действие
        FlowAction.objects.create(
            user_flow=user_flow,
            action_type=FlowAction.ActionType.PAUSED,
            performed_by=user,
            reason=self.validated_data.get('reason')
        )
        
        return user_flow


class QuizSubmissionSerializer(serializers.Serializer):
    """Сериализатор для ответа на вопрос квиза."""
    answer_id = serializers.PrimaryKeyRelatedField(
        queryset=QuizAnswer.objects.all(),
        label="ID ответа"
    )

    def validate(self, data):
        """Дополнительная валидация"""
        answer = data['answer_id']
        user_flow = self.context['user_flow']
        question = self.context['question']
        
        # Проверяем, что ответ принадлежит правильному вопросу
        if answer.question != question:
            raise serializers.ValidationError(
                "Выбранный ответ не принадлежит данному вопросу."
            )
            
        # Проверяем, что пользователь проходит именно этот поток
        if user_flow.flow != question.quiz.flow_step.flow:
            raise serializers.ValidationError(
                "Пользователь не проходит данный поток."
            )

        return data
        

class MyFlowProgressSerializer(serializers.ModelSerializer):
    """
    Сериализатор прогресса пользователя (для эндпоинта /api/my/)
    """
    flow = FlowBasicSerializer(read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    current_step_title = serializers.CharField(
        source='current_step.title',
        read_only=True
    )
    
    class Meta:
        model = UserFlow
        fields = [
            'id', 'flow', 'status', 'progress_percentage', 'is_overdue',
            'current_step_title', 'expected_completion_date',
            'started_at', 'completed_at', 'updated_at'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at', 'updated_at']