import React, { useState } from 'react';
import { 
  User, 
  BookOpen, 
  Target, 
  HelpCircle, 
  Clock, 
  CheckCircle, 
  Lock,
  Play,
  Star,
  Trophy,
  Calendar,
  TrendingUp,
  Zap,
  Coffee,
  Brain,
  ChevronRight,
  Award,
  Flag,
  MapPin,
  Users,
  MessageCircle,
  Sparkles
} from 'lucide-react';

// Компонент Step Card для пользователя
const UserStepCard = ({ step, progress, stepNumber, onStartStep, isAccessible, isNext }) => {
  const getStepIcon = (type) => {
    switch (type) {
      case 'article': return <BookOpen className="w-6 h-6" />;
      case 'task': return <Target className="w-6 h-6" />;
      case 'quiz': return <HelpCircle className="w-6 h-6" />;
      default: return <BookOpen className="w-6 h-6" />;
    }
  };

  const getStepColor = (type) => {
    switch (type) {
      case 'article': return 'blue';
      case 'task': return 'purple';
      case 'quiz': return 'emerald';
      default: return 'gray';
    }
  };

  const color = getStepColor(step.step_type);
  const isCompleted = progress?.status === 'completed';
  const isInProgress = progress?.status === 'in_progress';
  const isLocked = !isAccessible;

  return (
    <div className={`relative bg-white rounded-2xl shadow-lg border-2 transition-all duration-300 hover:shadow-xl ${
      isNext ? `border-${color}-400 ring-2 ring-${color}-100` : 
      isCompleted ? 'border-green-300' : 
      isLocked ? 'border-gray-200' : 'border-gray-200 hover:border-gray-300'
    }`}>
      {/* Next Step Badge */}
      {isNext && (
        <div className={`absolute -top-3 left-4 bg-${color}-500 text-white px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1`}>
          <Sparkles className="w-3 h-3" />
          Следующий этап
        </div>
      )}

      {/* Completed Badge */}
      {isCompleted && (
        <div className="absolute -top-3 right-4 bg-green-500 text-white p-2 rounded-full">
          <CheckCircle className="w-4 h-4" />
        </div>
      )}

      <div className="p-6">
        <div className="flex items-start gap-4">
          {/* Step Number & Icon */}
          <div className={`relative flex items-center justify-center w-14 h-14 rounded-xl ${
            isCompleted ? 'bg-green-100' :
            isInProgress ? `bg-${color}-100` :
            isLocked ? 'bg-gray-100' : `bg-${color}-50`
          }`}>
            {isLocked ? (
              <Lock className="w-6 h-6 text-gray-400" />
            ) : isCompleted ? (
              <CheckCircle className="w-6 h-6 text-green-600" />
            ) : (
              getStepIcon(step.step_type)
            )}
            
            <div className={`absolute -bottom-1 -right-1 w-6 h-6 rounded-full text-xs font-bold flex items-center justify-center ${
              isCompleted ? 'bg-green-500 text-white' :
              `bg-${color}-500 text-white`
            }`}>
              {stepNumber}
            </div>
          </div>
          
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className={`text-xs font-medium px-2 py-1 rounded-full uppercase tracking-wider ${
                isCompleted ? 'bg-green-100 text-green-700' :
                isInProgress ? `bg-${color}-100 text-${color}-700` :
                isLocked ? 'bg-gray-100 text-gray-500' :
                `bg-${color}-50 text-${color}-600`
              }`}>
                {step.step_type}
              </span>
              
              {step.is_required && (
                <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded-full">
                  Обязательный
                </span>
              )}
            </div>
            
            <h3 className={`font-bold text-lg mb-2 ${isLocked ? 'text-gray-400' : 'text-gray-900'}`}>
              {step.title}
            </h3>
            
            <p className={`text-sm mb-4 leading-relaxed ${isLocked ? 'text-gray-400' : 'text-gray-600'}`}>
              {step.description}
            </p>
            
            {/* Progress info */}
            {progress && (
              <div className="space-y-2 mb-4">
                {progress.started_at && (
                  <div className="text-xs text-gray-500 flex items-center gap-1">
                    <Play className="w-3 h-3" />
                    Начато: {new Date(progress.started_at).toLocaleDateString()}
                  </div>
                )}
                
                {isCompleted && progress.completed_at && (
                  <div className="text-xs text-green-600 flex items-center gap-1">
                    <CheckCircle className="w-3 h-3" />
                    Завершено: {new Date(progress.completed_at).toLocaleDateString()}
                  </div>
                )}
                
                {step.step_type === 'quiz' && progress.quiz_score !== null && (
                  <div className="text-xs text-emerald-600 flex items-center gap-1">
                    <Trophy className="w-3 h-3" />
                    Результат: {progress.quiz_score}%
                  </div>
                )}
              </div>
            )}
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 text-sm text-gray-500">
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {step.estimated_time_minutes}м
                </div>
              </div>
              
              {!isLocked && (
                <button
                  onClick={() => onStartStep(step)}
                  disabled={isCompleted}
                  className={`px-4 py-2 rounded-xl font-semibold transition-all flex items-center gap-2 ${
                    isCompleted 
                      ? 'bg-green-100 text-green-700 cursor-default'
                      : isInProgress
                      ? `bg-${color}-500 hover:bg-${color}-600 text-white hover:shadow-lg transform hover:scale-105`
                      : `bg-${color}-500 hover:bg-${color}-600 text-white hover:shadow-lg transform hover:scale-105`
                  }`}
                >
                  {isCompleted ? (
                    <>
                      <CheckCircle className="w-4 h-4" />
                      Завершено
                    </>
                  ) : isInProgress ? (
                    <>
                      <Play className="w-4 h-4" />
                      Продолжить
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      Начать
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Компонент Progress Bar
const ProgressBar = ({ current, total, color = 'blue' }) => {
  const percentage = Math.round((current / total) * 100);
  
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-gray-600">Прогресс</span>
        <span className={`font-semibold text-${color}-600`}>{percentage}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
        <div 
          className={`bg-gradient-to-r from-${color}-500 to-${color}-600 h-3 rounded-full transition-all duration-500 ease-out`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <div className="text-xs text-gray-500">
        {current} из {total} этапов завершено
      </div>
    </div>
  );
};

// Главный компонент User Flow Dashboard
const UserFlowDashboard = () => {
  const [activeTab, setActiveTab] = useState('flow'); // 'flow' | 'achievements' | 'help'

  // Данные пользователя
  const userData = {
    name: "Анна Иванова",
    position: "Junior UX Designer",
    avatar: null,
    level: 2,
    experience: 750,
    nextLevelXp: 1000
  };

  // Данные потока
  const flowData = {
    id: 1,
    title: "Онбординг нового дизайнера",
    description: "Комплексный курс введения в работу дизайн-команды компании",
    buddy_name: "Петр Смирнов",
    expected_completion: "2024-01-30",
    started_at: "2024-01-16"
  };

  // Этапы и прогресс
  const stepsData = [
    {
      step: {
        id: 1,
        title: "Знакомство с дизайн-системой",
        description: "Изучите основные принципы и компоненты нашей дизайн-системы для создания консистентных интерфейсов",
        step_type: "article",
        estimated_time_minutes: 45,
        is_required: true
      },
      progress: {
        status: "completed",
        started_at: "2024-01-16T09:30:00Z",
        completed_at: "2024-01-16T10:15:00Z"
      },
      isAccessible: true
    },
    {
      step: {
        id: 2,
        title: "Поиск в Figma файлах",
        description: "Найдите секретное кодовое слово в файлах дизайн-системы, чтобы показать знание структуры проекта",
        step_type: "task",
        estimated_time_minutes: 30,
        is_required: true
      },
      progress: {
        status: "completed",
        started_at: "2024-01-16T10:30:00Z",
        completed_at: "2024-01-16T11:00:00Z"
      },
      isAccessible: true
    },
    {
      step: {
        id: 3,
        title: "Тест по UI принципам",
        description: "Проверьте понимание основных принципов пользовательского интерфейса и лучших практик дизайна",
        step_type: "quiz",
        estimated_time_minutes: 20,
        is_required: true
      },
      progress: {
        status: "in_progress",
        started_at: "2024-01-17T09:00:00Z",
        quiz_score: null
      },
      isAccessible: true
    },
    {
      step: {
        id: 4,
        title: "Работа с компонентами",
        description: "Изучите как правильно использовать готовые компоненты и создавать новые на их основе",
        step_type: "article",
        estimated_time_minutes: 35,
        is_required: true
      },
      progress: null,
      isAccessible: true
    },
    {
      step: {
        id: 5,
        title: "Создание макета",
        description: "Примените полученные знания для создания простого макета страницы используя компоненты",
        step_type: "task",
        estimated_time_minutes: 60,
        is_required: true
      },
      progress: null,
      isAccessible: false
    },
    {
      step: {
        id: 6,
        title: "Финальная проверка",
        description: "Итоговый тест по всем изученным материалам для подтверждения полученных знаний",
        step_type: "quiz",
        estimated_time_minutes: 25,
        is_required: true
      },
      progress: null,
      isAccessible: false
    }
  ];

  // Подсчет статистики
  const completedSteps = stepsData.filter(s => s.progress?.status === 'completed').length;
  const totalSteps = stepsData.length;
  const nextStepIndex = stepsData.findIndex(s => s.progress?.status === 'in_progress' || (!s.progress && s.isAccessible));
  const currentStep = nextStepIndex >= 0 ? nextStepIndex + 1 : totalSteps;

  const handleStartStep = (step) => {
    console.log('Starting step:', step);
    // Здесь будет логика перехода к этапу
  };

  const achievements = [
    { id: 1, title: "Первый шаг", description: "Завершили первый этап", icon: <Flag className="w-5 h-5" />, earned: true },
    { id: 2, title: "Быстрый старт", description: "Завершили 2 этапа за день", icon: <Zap className="w-5 h-5" />, earned: true },
    { id: 3, title: "Знаток UI", description: "Пройдите тест на 90%+", icon: <Brain className="w-5 h-5" />, earned: false },
    { id: 4, title: "Мастер компонентов", description: "Изучите все компоненты", icon: <Award className="w-5 h-5" />, earned: false }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-white text-xl font-bold">
                {userData.name.charAt(0)}
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Привет, {userData.name.split(' ')[0]}! 👋</h1>
                <p className="text-gray-600">{userData.position}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="flex items-center gap-2">
                  <Star className="w-4 h-4 text-yellow-500" />
                  <span className="text-sm font-medium text-gray-700">Уровень {userData.level}</span>
                </div>
                <div className="text-xs text-gray-500">{userData.experience}/{userData.nextLevelXp} XP</div>
              </div>
              
              <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
                <MessageCircle className="w-6 h-6" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Flow Overview */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 mb-8">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">{flowData.title}</h2>
              <p className="text-gray-600 max-w-2xl">{flowData.description}</p>
            </div>
            
            <div className="text-right">
              <div className="text-sm text-gray-500 mb-1">Ваш наставник:</div>
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4 text-blue-500" />
                <span className="font-medium text-blue-600">{flowData.buddy_name}</span>
              </div>
            </div>
          </div>
          
          <ProgressBar current={completedSteps} total={totalSteps} color="blue" />
          
          <div className="grid grid-cols-3 gap-4 mt-6">
            <div className="text-center p-4 bg-blue-50 rounded-xl">
              <div className="text-2xl font-bold text-blue-600">{currentStep}</div>
              <div className="text-sm text-blue-700">Текущий этап</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-xl">
              <div className="text-2xl font-bold text-green-600">{completedSteps}</div>
              <div className="text-sm text-green-700">Завершено</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-xl">
              <div className="text-2xl font-bold text-purple-600">{totalSteps - completedSteps}</div>
              <div className="text-sm text-purple-700">Осталось</div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mb-8 bg-gray-100 p-1 rounded-xl w-fit">
          <button
            onClick={() => setActiveTab('flow')}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              activeTab === 'flow' 
                ? 'bg-white text-blue-600 shadow-sm' 
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            Этапы обучения
          </button>
          <button
            onClick={() => setActiveTab('achievements')}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              activeTab === 'achievements' 
                ? 'bg-white text-blue-600 shadow-sm' 
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            Достижения
          </button>
          <button
            onClick={() => setActiveTab('help')}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              activeTab === 'help' 
                ? 'bg-white text-blue-600 shadow-sm' 
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            Помощь
          </button>
        </div>

        {/* Flow Steps */}
        {activeTab === 'flow' && (
          <div className="space-y-6">
            {stepsData.map(({ step, progress, isAccessible }, index) => (
              <UserStepCard
                key={step.id}
                step={step}
                progress={progress}
                stepNumber={index + 1}
                onStartStep={handleStartStep}
                isAccessible={isAccessible}
                isNext={index === nextStepIndex}
              />
            ))}
          </div>
        )}

        {/* Achievements */}
        {activeTab === 'achievements' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {achievements.map((achievement) => (
              <div
                key={achievement.id}
                className={`p-6 rounded-2xl border-2 transition-all ${
                  achievement.earned
                    ? 'bg-gradient-to-br from-yellow-50 to-orange-50 border-yellow-300'
                    : 'bg-gray-50 border-gray-200'
                }`}
              >
                <div className="flex items-start gap-4">
                  <div className={`p-3 rounded-xl ${
                    achievement.earned ? 'bg-yellow-100 text-yellow-600' : 'bg-gray-200 text-gray-400'
                  }`}>
                    {achievement.icon}
                  </div>
                  <div className="flex-1">
                    <h3 className={`font-bold ${achievement.earned ? 'text-gray-900' : 'text-gray-500'}`}>
                      {achievement.title}
                    </h3>
                    <p className={`text-sm ${achievement.earned ? 'text-gray-700' : 'text-gray-400'}`}>
                      {achievement.description}
                    </p>
                    {achievement.earned && (
                      <div className="mt-2 flex items-center gap-1 text-xs text-yellow-600">
                        <Trophy className="w-3 h-3" />
                        Получено!
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Help */}
        {activeTab === 'help' && (
          <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <MessageCircle className="w-5 h-5 text-blue-500" />
                Связь с наставником
              </h3>
              <p className="text-gray-600 mb-4">
                Если у вас есть вопросы или нужна помощь, обратитесь к своему наставнику.
              </p>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 font-medium text-sm">{flowData.buddy_name.charAt(0)}</span>
                  </div>
                  <span className="font-medium text-gray-900">{flowData.buddy_name}</span>
                </div>
                <button className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors">
                  Написать сообщение
                </button>
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Часто задаваемые вопросы</h3>
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-gray-900 mb-1">Как начать следующий этап?</h4>
                  <p className="text-sm text-gray-600">Этапы открываются последовательно после завершения предыдущих.</p>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 mb-1">Что делать если тест не проходится?</h4>
                  <p className="text-sm text-gray-600">Можно пересдать тест несколько раз. Изучите материалы еще раз.</p>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 mb-1">Как получить достижения?</h4>
                  <p className="text-sm text-gray-600">Достижения открываются автоматически при выполнении условий.</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserFlowDashboard;