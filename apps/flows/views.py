"""
Представления для системы потоков обучения
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, Count, Avg, Case, When, Value, FloatField
from django.db.models.functions import Cast
from rest_framework.exceptions import PermissionDenied

from .models import (
    Flow, FlowStep, Task, Quiz, QuizQuestion, QuizAnswer,
    UserFlow, FlowBuddy, UserStepProgress, UserQuizAnswer, FlowAction,
    TaskSnapshot, QuizSnapshot, QuizQuestionSnapshot
)
from .snapshot_models import QuizAnswerSnapshot, UserQuizAnswerSnapshot
from .serializers import (
    FlowSerializer, FlowDetailSerializer, FlowStepSerializer,
    TaskSerializer, TaskAnswerSerializer, QuizSerializer,
    UserFlowSerializer, UserFlowDetailSerializer, UserFlowStartSerializer,
    UserStepProgressSerializer, FlowPauseSerializer, QuizSubmissionSerializer,
    MyFlowProgressSerializer, FlowActionSerializer
)
from apps.common.permissions import (
    IsActiveUser, IsModerator, IsBuddyOrModerator, CanManageFlow,
    CanViewUserProgress, CanAccessFlowStep
)


# ========== Представления для обычных пользователей (API /my/) ==========

class MyFlowListView(generics.ListAPIView):
    """
    Мои доступные потоки обучения
    """
    serializer_class = MyFlowProgressSerializer
    permission_classes = [IsActiveUser]
    
    def get_queryset(self):
        """Возвращает потоки текущего пользователя"""
        return UserFlow.objects.for_user(self.request.user).select_related('flow').order_by('-created_at')


class MyFlowProgressView(APIView):
    """
    Мой прогресс.
    - GET /api/my/progress/ - Агрегированный прогресс по всем потокам.
    - GET /api/my/progress/{flow_id}/ - Детальный прогресс по одному потоку.
    """
    permission_classes = [IsActiveUser]

    def get(self, request, *args, **kwargs):
        flow_id = kwargs.get('pk')
        user = request.user

        if flow_id:
            # Детальный прогресс по одному потоку
            user_flow = get_object_or_404(UserFlow, flow_id=flow_id, user=user)
            serializer = UserFlowDetailSerializer(user_flow, context={'request': request})
            return Response(serializer.data)
        else:
            # Агрегированный прогресс по всем потокам
            user_flows = UserFlow.objects.for_user(user)
            if not user_flows.exists():
                return Response({
                    "total_flows": 0,
                    "completed_flows": 0,
                    "in_progress_flows": 0,
                    "average_progress": 0
                })
            
            # Аннотируем каждый UserFlow вычисленным прогрессом
            annotated_flows = user_flows.annotate(
                completed_steps_count=Count(
                    'step_progress', 
                    filter=Q(step_progress__status=UserStepProgress.StepStatus.COMPLETED)
                ),
                total_steps_count=Count('flow__flow_steps', filter=Q(flow__flow_steps__is_active=True))
            ).annotate(
                progress=Case(
                    When(total_steps_count=0, then=Value(100.0)),
                    default=(
                        Cast('completed_steps_count', FloatField()) * 100.0 / 
                        Cast('total_steps_count', FloatField())
                    ),
                    output_field=FloatField()
                )
            )

            aggregation = annotated_flows.aggregate(
                total_flows=Count('id'),
                completed_flows=Count('id', filter=Q(status=UserFlow.FlowStatus.COMPLETED)),
                average_progress=Avg('progress')
            )
            
            return Response({
                "total_flows": aggregation['total_flows'],
                "completed_flows": aggregation['completed_flows'],
                "in_progress_flows": aggregation['total_flows'] - aggregation['completed_flows'],
                "average_progress": round(aggregation['average_progress'] or 0, 2)
            })


# ========== Публичные представления для потоков ==========

class FlowDetailView(generics.RetrieveAPIView):
    """
    Детали потока обучения
    """
    queryset = Flow.objects.active()
    serializer_class = FlowDetailSerializer
    permission_classes = [IsActiveUser]


class FlowStepListView(generics.ListAPIView):
    """
    Этапы потока (только доступные для текущего пользователя)
    """
    serializer_class = FlowStepSerializer
    permission_classes = [IsActiveUser]
    
    def get_queryset(self):
        flow_id = self.kwargs['flow_id']
        flow = get_object_or_404(Flow, id=flow_id, is_active=True)
        
        # Получаем UserFlow для текущего пользователя
        try:
            user_flow = UserFlow.objects.get(user=self.request.user, flow=flow)
        except UserFlow.DoesNotExist:
            return FlowStep.objects.none()
        
        # Возвращаем все этапы с информацией о доступности
        return flow.flow_steps.filter(is_active=True).order_by('order')


class FlowStepReadView(APIView):
    """
    Отметка этапа как прочитанного
    """
    permission_classes = [IsActiveUser]
    
    def post(self, request, flow_id, step_id):
        """
        Отмечает этап как прочитанный при первом открытии
        """
        flow = get_object_or_404(Flow, id=flow_id, is_active=True)
        step = get_object_or_404(FlowStep, id=step_id, flow=flow, is_active=True)
        
        try:
            user_flow = UserFlow.objects.get(user=request.user, flow=flow)
        except UserFlow.DoesNotExist:
            return Response({
                'error': 'Поток не назначен пользователю'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            step_progress = UserStepProgress.objects.get(
                user_flow=user_flow,
                flow_step=step
            )
            
            # Проверяем доступность этапа
            if not step_progress.is_accessible:
                return Response({
                    'error': 'Этап недоступен'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Отмечаем как начатый, если еще не начат
            if step_progress.status == UserStepProgress.StepStatus.AVAILABLE:
                step_progress.status = UserStepProgress.StepStatus.IN_PROGRESS
                step_progress.started_at = timezone.now()
            
            # Отмечаем статью как прочитанную
            if step.step_type == FlowStep.StepType.ARTICLE and not step_progress.article_read_at:
                step_progress.article_read_at = timezone.now()
                
                # Если это только статья, завершаем этап
                if step.step_type == FlowStep.StepType.ARTICLE:
                    step_progress.status = UserStepProgress.StepStatus.COMPLETED
                    step_progress.completed_at = timezone.now()
                    
                    # Записываем действие
                    FlowAction.objects.create(
                        user_flow=user_flow,
                        action_type=FlowAction.ActionType.STEP_COMPLETED,
                        performed_by=request.user,
                        metadata={'step_id': step.id, 'step_title': step.title}
                    )
                    
                    # Разблокируем следующий этап
                    self._unlock_next_step(user_flow, step)
            
            step_progress.save()
            
            return Response({
                'message': 'Этап отмечен как прочитанный',
                'step_progress': UserStepProgressSerializer(step_progress).data
            })
            
        except UserStepProgress.DoesNotExist:
            return Response({
                'error': 'Прогресс по этапу не найден'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def _unlock_next_step(self, user_flow, current_step):
        """Разблокирует следующий этап"""
        next_step = FlowStep.objects.filter(
            flow=current_step.flow,
            order=current_step.order + 1,
            is_active=True
        ).first()
        
        if next_step:
            next_progress, created = UserStepProgress.objects.get_or_create(
                user_flow=user_flow,
                flow_step=next_step,
                defaults={'status': UserStepProgress.StepStatus.AVAILABLE}
            )
            
            if next_progress.status == UserStepProgress.StepStatus.LOCKED:
                next_progress.status = UserStepProgress.StepStatus.AVAILABLE
                next_progress.save()


class FlowStepTaskView(APIView):
    """
    Получение задания и отправка ответа
    """
    permission_classes = [IsActiveUser, CanAccessFlowStep]
    
    def get(self, request, flow_id, step_id):
        """
        Получение задания для этапа
        """
        step = self.get_step(flow_id, step_id)
        
        if step.step_type != FlowStep.StepType.TASK:
            return Response({
                'error': 'Этап не содержит задания'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not hasattr(step, 'task'):
            return Response({
                'error': 'Задание не найдено'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TaskSerializer(step.task, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request, flow_id, step_id):
        """
        Отправка ответа на задание
        """
        step = self.get_step(flow_id, step_id)
        user_flow = self.get_user_flow(flow_id)
        
        if step.step_type != FlowStep.StepType.TASK:
            return Response({
                'error': 'Этап не содержит задания'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not hasattr(step, 'task'):
            return Response({
                'error': 'Задание не найдено'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TaskAnswerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        answer = serializer.validated_data['answer']
        task = step.task
        
        # Создаем снапшот задания
        task_snapshot = TaskSnapshot.objects.create(
            user_progress=user_flow,
            task_title=task.title,
            task_description=task.description,
            task_instruction=task.instruction,
            task_code_word=task.code_word,
            task_hint=task.hint,
            user_answer=answer,
            is_correct=answer.lower() == task.code_word.lower(),
            attempts_count=1
        )
        
        # Проверяем ответ
        is_correct = answer.lower() == task.code_word.lower()
        
        # Обновляем прогресс
        step_progress = UserStepProgress.objects.get(
            user_flow=user_flow,
            flow_step=step
        )
        
        if is_correct:
            step_progress.status = UserStepProgress.StepStatus.COMPLETED
            step_progress.completed_at = timezone.now()
            
            # Записываем действие
            FlowAction.objects.create(
                user_flow=user_flow,
                action_type=FlowAction.ActionType.STEP_COMPLETED,
                performed_by=request.user,
                metadata={'step_id': step.id, 'step_title': step.title}
            )
            
            # Разблокируем следующий этап
            self._unlock_next_step(user_flow, step)
        
        step_progress.save()
        
        return Response({
            'is_correct': is_correct,
            'message': 'Правильно!' if is_correct else 'Неправильно, попробуйте еще раз',
            'step_progress': UserStepProgressSerializer(step_progress).data
        })
    
    def get_step(self, flow_id, step_id):
        """Получает этап с проверкой доступности"""
        flow = get_object_or_404(Flow, id=flow_id, is_active=True)
        return get_object_or_404(FlowStep, id=step_id, flow=flow, is_active=True)
    
    def get_user_flow(self, flow_id):
        """Получает UserFlow для текущего пользователя"""
        flow = get_object_or_404(Flow, id=flow_id, is_active=True)
        return get_object_or_404(UserFlow, user=self.request.user, flow=flow)
    
    def _unlock_next_step(self, user_flow, current_step):
        """Разблокирует следующий этап"""
        next_step = FlowStep.objects.filter(
            flow=current_step.flow,
            order=current_step.order + 1,
            is_active=True
        ).first()
        
        if next_step:
            next_progress, created = UserStepProgress.objects.get_or_create(
                user_flow=user_flow,
                flow_step=next_step,
                defaults={'status': UserStepProgress.StepStatus.AVAILABLE}
            )
            
            if next_progress.status == UserStepProgress.StepStatus.LOCKED:
                next_progress.status = UserStepProgress.StepStatus.AVAILABLE
                next_progress.save()


class FlowStepQuizView(APIView):
    """
    Получение квиза и отправка ответов
    """
    permission_classes = [IsActiveUser, CanAccessFlowStep]
    
    def get(self, request, flow_id, step_id):
        """
        Получение квиза для этапа
        """
        step = self.get_step(flow_id, step_id)
        
        if step.step_type != FlowStep.StepType.QUIZ:
            return Response({
                'error': 'Этап не содержит квиза'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not hasattr(step, 'quiz'):
            return Response({
                'error': 'Квиз не найден'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = QuizSerializer(step.quiz, context={'request': request})
        return Response(serializer.data)
    
    def get_step(self, flow_id, step_id):
        """Получает этап с проверкой доступности"""
        flow = get_object_or_404(Flow, id=flow_id, is_active=True)
        return get_object_or_404(FlowStep, id=step_id, flow=flow, is_active=True)


class QuizQuestionAnswerView(APIView):
    """
    Отправка ответа на вопрос квиза
    """
    permission_classes = [IsActiveUser]
    
    def post(self, request, flow_id, step_id, question_id):
        """
        Сохраняет ответ пользователя на вопрос квиза
        """
        step = get_object_or_404(FlowStep, id=step_id, flow_id=flow_id, is_active=True)
        user_flow = get_object_or_404(UserFlow, flow_id=flow_id, user=request.user)
        
        if step.step_type != FlowStep.StepType.QUIZ:
            return Response({
                'error': 'Этап не содержит квиза'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not hasattr(step, 'quiz'):
            return Response({
                'error': 'Квиз не найден'
            }, status=status.HTTP_404_NOT_FOUND)
        
        question = get_object_or_404(QuizQuestion, id=question_id, quiz=step.quiz)
        
        serializer = QuizSubmissionSerializer(
            data=request.data,
            context={
                'request': request, 
                'user_flow': user_flow,
                'question': question
            }
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        answer = serializer.validated_data['answer_id']
        
        # Сохраняем ответ пользователя
        user_answer, created = UserQuizAnswer.objects.update_or_create(
            user_flow=user_flow,
            question=question,
            defaults={
                'selected_answer': answer,
                'is_correct': answer.is_correct,
                'answered_at': timezone.now()
            }
        )
        
        # Проверяем завершение квиза
        is_completed = self._check_quiz_completion(user_flow, step, step.quiz)
        
        return Response({
            'message': 'Ответ сохранен',
            'is_correct': answer.is_correct,
            'is_completed': is_completed
        })
    
    def _check_quiz_completion(self, user_flow, step, quiz):
        """
        Проверяет завершение квиза и создает снапшоты
        """
        # Получаем все ответы пользователя на вопросы квиза
        user_answers = UserQuizAnswer.objects.filter(
            user_flow=user_flow,
            question__quiz=quiz
        )
        
        # Проверяем, что ответил на все вопросы
        total_questions = quiz.questions.count()
        if user_answers.count() < total_questions:
            return False
        
        # Создаем снапшоты и завершаем квиз
        is_passed = self.complete_quiz_step(user_flow, step, user_answers)
        return is_passed
    
    def complete_quiz_step(self, user_flow, step, user_quiz_answers):
        """
        Завершение этапа с квизом с созданием полного снапшота
        """
        quiz = step.quiz
        
        # Получаем прогресс по этапу
        step_progress, created = UserStepProgress.objects.get_or_create(
            user_flow=user_flow,
            flow_step=step
        )
        
        # Создаем снапшот квиза
        quiz_snapshot = QuizSnapshot.objects.create(
            user_step_progress=step_progress,
            quiz_title=quiz.title,
            quiz_description=quiz.description or '',
            passing_score_percentage=quiz.passing_score_percentage,
            total_questions=quiz.questions.count(),
            correct_answers=0,  # Пока 0, пересчитаем ниже
            score_percentage=0,  # Пока 0, пересчитаем ниже
            is_passed=False  # Пока False, пересчитаем ниже
        )
        
        correct_count = 0
        
        # Создаем снапшоты для каждого вопроса
        for question in quiz.questions.all().order_by('order'):
            # Снапшот вопроса
            question_snapshot = QuizQuestionSnapshot.objects.create(
                quiz_snapshot=quiz_snapshot,
                original_question_id=question.id,
                question_text=question.question,
                question_order=question.order,
                explanation=question.explanation or ''
            )
            
            # Снапшоты всех вариантов ответов для этого вопроса
            answer_snapshots = {}
            for answer in question.answers.all().order_by('order'):
                answer_snapshot = QuizAnswerSnapshot.objects.create(
                    question_snapshot=question_snapshot,
                    original_answer_id=answer.id,
                    answer_text=answer.answer_text,
                    is_correct=answer.is_correct,
                    answer_order=answer.order,
                    explanation=answer.explanation or ''
                )
                answer_snapshots[answer.id] = answer_snapshot
            
            # Ищем ответ пользователя на этот вопрос
            user_answer = user_quiz_answers.filter(question=question).first()
            if user_answer:
                selected_answer_snapshot = answer_snapshots[user_answer.selected_answer.id]
                
                # Создаем снапшот ответа пользователя
                UserQuizAnswerSnapshot.objects.create(
                    quiz_snapshot=quiz_snapshot,
                    question_snapshot=question_snapshot,
                    selected_answer_snapshot=selected_answer_snapshot,
                    is_correct=user_answer.is_correct,
                    answered_at=user_answer.answered_at
                )
                
                if user_answer.is_correct:
                    correct_count += 1
        
        # Обновляем результаты в снапшоте квиза
        total_questions = quiz.questions.count()
        score_percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
        is_passed = score_percentage >= quiz.passing_score_percentage
        
        quiz_snapshot.correct_answers = correct_count
        quiz_snapshot.score_percentage = int(score_percentage)
        quiz_snapshot.is_passed = is_passed
        quiz_snapshot.save()
        
        # Обновляем прогресс по этапу
        step_progress.quiz_completed_at = timezone.now()
        step_progress.quiz_correct_answers = correct_count
        step_progress.quiz_total_questions = total_questions
        
        if is_passed:
            step_progress.status = UserStepProgress.StepStatus.COMPLETED
            step_progress.completed_at = step_progress.quiz_completed_at
            
            # Разблокируем следующий этап
            self._unlock_next_step(user_flow, step)
        
        step_progress.save()
        return is_passed
    
    def _unlock_next_step(self, user_flow, current_step):
        """Разблокирует следующий этап"""
        next_step = FlowStep.objects.filter(
            flow=current_step.flow,
            order=current_step.order + 1,
            is_active=True
        ).first()
        
        if next_step:
            next_progress, created = UserStepProgress.objects.get_or_create(
                user_flow=user_flow,
                flow_step=next_step,
                defaults={'status': UserStepProgress.StepStatus.AVAILABLE}
            )
            
            if next_progress.status == UserStepProgress.StepStatus.LOCKED:
                next_progress.status = UserStepProgress.StepStatus.AVAILABLE
                next_progress.save()


# ========== Представления для Buddy ==========

class BuddyFlowListView(generics.ListAPIView):
    """
    Список доступных потоков для запуска (только для buddy)
    """
    serializer_class = FlowSerializer
    permission_classes = [IsBuddyOrModerator]
    
    def get_queryset(self):
        return Flow.objects.active().order_by('title')


class BuddyUserListView(generics.ListAPIView):
    """
    Список пользователей для назначения потоков (только для buddy)
    """
    from apps.users.serializers import UserListSerializer
    
    serializer_class = UserListSerializer
    permission_classes = [IsBuddyOrModerator]
    
    def get_queryset(self):
        from apps.users.models import User
        return User.objects.active_users().order_by('name')


class BuddyFlowStartView(generics.CreateAPIView):
    """
    Запуск потока для пользователя (только для buddy)
    """
    serializer_class = UserFlowStartSerializer
    permission_classes = [IsBuddyOrModerator]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['flow'] = get_object_or_404(Flow, pk=self.kwargs['pk'])
        return context

    def create(self, request, *args, **kwargs):
        flow = get_object_or_404(Flow, pk=self.kwargs['pk'])
        user_id = request.data.get('user_id')

        # Проверяем, не запущен ли уже поток для этого пользователя
        if UserFlow.objects.filter(
            user_id=user_id,
            flow=flow,
            status__in=[UserFlow.FlowStatus.IN_PROGRESS, UserFlow.FlowStatus.PAUSED]
        ).exists():
            return Response(
                {'error': 'Для этого пользователя уже запущен этот поток.'},
                status=status.HTTP_409_CONFLICT
            )
        return super().create(request, *args, **kwargs)


class BuddyMyFlowsView(generics.ListAPIView):
    """
    Потоки где я являюсь buddy
    """
    serializer_class = UserFlowSerializer
    permission_classes = [IsBuddyOrModerator]
    
    def get_queryset(self):
        """Возвращает потоки, где текущий пользователь является бадди"""
        user = self.request.user
        return UserFlow.objects.filter(flow_buddies__buddy_user=user, flow_buddies__is_active=True)


class BuddyFlowManageView(generics.RetrieveDestroyAPIView):
    """
    Просмотр и удаление (остановка) потока подопечного.
    Обрабатывает GET для получения деталей и DELETE для удаления.
    """
    serializer_class = UserFlowDetailSerializer
    permission_classes = [IsBuddyOrModerator, CanManageFlow]
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        """Доступ только к потокам, где пользователь является бадди."""
        user = self.request.user
        return UserFlow.objects.filter(
            flow_buddies__buddy_user=user,
            flow_buddies__is_active=True
        ).distinct()
    
    def perform_destroy(self, instance):
        """
        При удалении создается запись в истории.
        """
        FlowAction.objects.create(
            user_flow=instance,
            action_type=FlowAction.ActionType.DELETED,
            performed_by=self.request.user,
            reason="Flow deleted by buddy."
        )
        instance.delete()


class BuddyFlowPauseView(APIView):
    """
    Приостановка потока buddy
    """
    permission_classes = [IsBuddyOrModerator, CanManageFlow]

    def post(self, request, pk):
        serializer = FlowPauseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reason = serializer.validated_data.get('reason')
        
        user_flow = self.get_user_flow(pk)
        user_flow.pause(paused_by=request.user, reason=reason)
        
        return Response({'status': 'paused'}, status=status.HTTP_200_OK)

    def get_user_flow(self, pk):
        """Получает UserFlow по pk и проверяет права"""
        user_flow = get_object_or_404(UserFlow, pk=pk)
        # Проверяем, что текущий бадди управляет этим потоком
        if not FlowBuddy.objects.filter(user_flow=user_flow, buddy_user=self.request.user).exists():
            raise PermissionDenied("Вы не являетесь бадди этого потока.")
        return user_flow


class BuddyFlowResumeView(APIView):
    """
    Возобновление потока buddy
    """
    permission_classes = [IsBuddyOrModerator, CanManageFlow]

    def post(self, request, pk):
        user_flow = self.get_user_flow(pk)
        user_flow.resume()
        return Response({'status': 'in_progress'}, status=status.HTTP_200_OK)

    def get_user_flow(self, pk):
        """Получает UserFlow по pk и проверяет права"""
        user_flow = get_object_or_404(UserFlow, pk=pk)
        # Проверяем, что текущий бадди управляет этим потоком
        if not FlowBuddy.objects.filter(user_flow=user_flow, buddy_user=self.request.user).exists():
            raise PermissionDenied("Вы не являетесь бадди этого потока.")
        return user_flow


# ========== Представления для модераторов ==========

class AdminFlowListView(generics.ListCreateAPIView):
    """
    Управление потоками (только модераторы)
    """
    queryset = Flow.objects.active().order_by('title')
    serializer_class = FlowSerializer
    permission_classes = [IsModerator]


class AdminFlowDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детальное управление потоком (только модераторы)
    """
    queryset = Flow.objects.active()
    serializer_class = FlowDetailSerializer
    permission_classes = [IsModerator]
    
    def perform_destroy(self, instance):
        """Мягкое удаление потока"""
        instance.delete()


class AdminFlowStepListView(generics.ListCreateAPIView):
    """
    Управление этапами потока (только модераторы)
    """
    serializer_class = FlowStepSerializer
    permission_classes = [IsModerator]
    
    def get_queryset(self):
        flow_id = self.kwargs['flow_id']
        flow = get_object_or_404(Flow, id=flow_id, is_active=True)
        return flow.flow_steps.filter(is_active=True).order_by('order')
    
    def perform_create(self, serializer):
        flow_id = self.kwargs['flow_id']
        flow = get_object_or_404(Flow, id=flow_id, is_active=True)
        
        # Устанавливаем порядок для нового этапа
        serializer.save(
            flow=flow,
            order=flow.get_next_step_order()
        )


class AdminFlowStepDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детальное управление этапом потока (только модераторы)
    """
    queryset = FlowStep.objects.filter(is_active=True)
    serializer_class = FlowStepSerializer
    permission_classes = [IsModerator]
    
    def perform_destroy(self, instance):
        """Мягкое удаление этапа"""
        instance.delete()


# ========== Аналитика и отчеты ==========

class AdminAnalyticsOverviewView(APIView):
    """
    Общая статистика системы (только модераторы)
    """
    permission_classes = [IsModerator]
    
    def get(self, request):
        """
        Возвращает общую статистику системы
        """
        from apps.users.models import User
        
        # Статистика пользователей
        total_users = User.objects.active_users().count()
        active_flows = UserFlow.objects.in_progress().count()
        completed_flows = UserFlow.objects.completed().count()
        overdue_flows = UserFlow.objects.overdue().count()
        
        # Статистика потоков
        total_flows = Flow.objects.active().count()
        
        # Средняя завершаемость
        completion_rate = 0
        if UserFlow.objects.active().count() > 0:
            completion_rate = (completed_flows / UserFlow.objects.active().count()) * 100
        
        return Response({
            'users': {
                'total': total_users,
                'with_active_flows': active_flows,
                'completed_flows': completed_flows,
                'overdue_flows': overdue_flows
            },
            'flows': {
                'total': total_flows,
                'completion_rate': round(completion_rate, 2)
            },
            'recent_activity': self._get_recent_activity()
        })
    
    def _get_recent_activity(self):
        """Получает недавнюю активность"""
        recent_actions = FlowAction.objects.select_related(
            'user_flow__user', 'user_flow__flow', 'performed_by'
        ).order_by('-performed_at')[:10]
        
        return FlowActionSerializer(recent_actions, many=True).data


@api_view(['GET'])
@permission_classes([IsModerator])
def flow_statistics(request):
    """
    Статистика по потокам
    """
    stats = UserFlow.objects.statistics_by_flow()
    return Response(list(stats))


@api_view(['GET'])
@permission_classes([IsModerator])
def problem_users_report(request):
    """
    Отчет по проблемным пользователям
    """
    problem_flows = UserFlow.objects.requiring_attention().select_related(
        'user', 'flow'
    )
    
    data = []
    for user_flow in problem_flows:
        data.append({
            'user': {
                'id': user_flow.user.id,
                'name': user_flow.user.name,
                'email': user_flow.user.email
            },
            'flow': {
                'id': user_flow.flow.id,
                'title': user_flow.flow.title
            },
            'status': user_flow.status,
            'is_overdue': user_flow.is_overdue,
            'progress_percentage': user_flow.progress_percentage,
            'expected_completion_date': user_flow.expected_completion_date,
            'last_activity': user_flow.updated_at
        })
    
    return Response(data)