import React, { useState } from 'react';
import { 
  Eye, 
  BookOpen, 
  Target, 
  HelpCircle, 
  Clock, 
  CheckCircle, 
  Users, 
  Play,
  ChevronRight,
  ChevronDown,
  ArrowLeft,
  Calendar,
  TrendingUp,
  FileText,
  Zap,
  Settings,
  BarChart3
} from 'lucide-react';

// Компонент для превью Step
const StepPreview = ({ step, stepNumber, onViewDetails, isSelected, progress }) => {
  const getStepIcon = (type) => {
    switch (type) {
      case 'article': return <BookOpen className="w-5 h-5" />;
      case 'task': return <Target className="w-5 h-5" />;
      case 'quiz': return <HelpCircle className="w-5 h-5" />;
      default: return <FileText className="w-5 h-5" />;
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
  const completionRate = progress ? Math.round((progress.completed / progress.total) * 100) : 0;

  return (
    <div 
      className={`bg-white rounded-xl border-2 transition-all duration-200 cursor-pointer hover:shadow-lg ${
        isSelected ? `border-${color}-500 shadow-lg` : 'border-gray-200 hover:border-gray-300'
      }`}
      onClick={() => onViewDetails(step)}
    >
      <div className="p-4">
        <div className="flex items-start gap-3">
          {/* Step Number & Icon */}
          <div className={`flex items-center justify-center w-10 h-10 rounded-lg bg-${color}-100`}>
            <span className={`text-sm font-bold text-${color}-600`}>{stepNumber}</span>
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <div className={`p-1 bg-${color}-100 rounded`}>
                {getStepIcon(step.step_type)}
              </div>
              <span className={`text-xs font-medium text-${color}-600 uppercase tracking-wider`}>
                {step.step_type}
              </span>
            </div>
            
            <h3 className="font-semibold text-gray-900 text-sm mb-1 line-clamp-2">
              {step.title}
            </h3>
            
            <p className="text-xs text-gray-600 line-clamp-2 mb-2">
              {step.description}
            </p>

            {/* Progress bar if progress data exists */}
            {progress && (
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-gray-600">Прогресс:</span>
                  <span className={`font-medium text-${color}-600`}>{completionRate}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                  <div 
                    className={`bg-${color}-500 h-1.5 rounded-full transition-all duration-300`}
                    style={{ width: `${completionRate}%` }}
                  />
                </div>
                <div className="text-xs text-gray-500">
                  {progress.completed} из {progress.total} завершили
                </div>
              </div>
            )}

            <div className="flex items-center justify-between mt-2">
              <div className="flex items-center gap-1 text-xs text-gray-500">
                <Clock className="w-3 h-3" />
                {step.estimated_time_minutes}м
              </div>
              
              <ChevronRight className="w-4 h-4 text-gray-400" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Подробный просмотр Step
const StepDetailView = ({ step, onBack, userProgress = [] }) => {
  const getStepColor = (type) => {
    switch (type) {
      case 'article': return 'blue';
      case 'task': return 'purple';
      case 'quiz': return 'emerald';
      default: return 'gray';
    }
  };

  const color = getStepColor(step.step_type);

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200">
      {/* Header */}
      <div className={`bg-gradient-to-r from-${color}-500 to-${color}-600 p-6 text-white`}>
        <div className="flex items-center gap-4 mb-4">
          <button
            onClick={onBack}
            className="p-2 hover:bg-white/20 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-medium bg-white/20 px-2 py-1 rounded uppercase tracking-wider">
                {step.step_type}
              </span>
              {step.is_required && (
                <span className="text-xs bg-red-500 px-2 py-1 rounded">Обязательный</span>
              )}
            </div>
            <h2 className="text-xl font-bold">{step.title}</h2>
          </div>
        </div>
        
        <div className="grid grid-cols-3 gap-4 text-center">
          <div className="bg-white/10 rounded-lg p-3">
            <Clock className="w-5 h-5 mx-auto mb-1" />
            <div className="text-sm font-semibold">{step.estimated_time_minutes}м</div>
            <div className="text-xs opacity-80">Время</div>
          </div>
          <div className="bg-white/10 rounded-lg p-3">
            <Users className="w-5 h-5 mx-auto mb-1" />
            <div className="text-sm font-semibold">{userProgress.length}</div>
            <div className="text-xs opacity-80">Пользователей</div>
          </div>
          <div className="bg-white/10 rounded-lg p-3">
            <TrendingUp className="w-5 h-5 mx-auto mb-1" />
            <div className="text-sm font-semibold">
              {userProgress.length > 0 
                ? Math.round((userProgress.filter(p => p.status === 'completed').length / userProgress.length) * 100)
                : 0}%
            </div>
            <div className="text-xs opacity-80">Завершили</div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        <div className="space-y-6">
          {/* Description */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Описание этапа:</h3>
            <p className="text-gray-700 leading-relaxed">{step.description}</p>
          </div>

          {/* Content Preview */}
          <div className="bg-gray-50 rounded-xl p-4">
            <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <Eye className="w-5 h-5" />
              Превью контента:
            </h3>
            
            {step.step_type === 'article' && step.article && (
              <div className="space-y-2">
                <h4 className="font-medium text-gray-800">{step.article.title}</h4>
                <div className="text-sm text-gray-600 prose-sm" 
                     dangerouslySetInnerHTML={{ 
                       __html: step.article.content.substring(0, 200) + '...' 
                     }} 
                />
              </div>
            )}
            
            {step.step_type === 'task' && step.task && (
              <div className="space-y-2">
                <h4 className="font-medium text-gray-800">{step.task.title}</h4>
                <p className="text-sm text-gray-600">{step.task.description}</p>
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                  <p className="text-sm text-purple-800">
                    <strong>Инструкция:</strong> {step.task.instruction}
                  </p>
                </div>
              </div>
            )}
            
            {step.step_type === 'quiz' && step.quiz && (
              <div className="space-y-2">
                <h4 className="font-medium text-gray-800">{step.quiz.title}</h4>
                <p className="text-sm text-gray-600">{step.quiz.description}</p>
                <div className="flex items-center gap-4 text-sm">
                  <span className="bg-emerald-100 text-emerald-800 px-2 py-1 rounded">
                    {step.quiz.questions?.length || 0} вопросов
                  </span>
                  <span className="bg-emerald-100 text-emerald-800 px-2 py-1 rounded">
                    Проходной балл: {step.quiz.passing_score_percentage}%
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* User Progress */}
          {userProgress.length > 0 && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Прогресс пользователей:
              </h3>
              
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {userProgress.map((progress, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center text-xs font-medium">
                        {progress.user.name.charAt(0)}
                      </div>
                      <div>
                        <div className="font-medium text-sm">{progress.user.name}</div>
                        <div className="text-xs text-gray-600">{progress.user.position}</div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        progress.status === 'completed' 
                          ? `bg-${color}-100 text-${color}-800`
                          : progress.status === 'in_progress'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-gray-100 text-gray-600'
                      }`}>
                        {progress.status === 'completed' ? 'Завершено' : 
                         progress.status === 'in_progress' ? 'В процессе' : 'Не начато'}
                      </span>
                      
                      {progress.status === 'completed' && (
                        <CheckCircle className={`w-4 h-4 text-${color}-600`} />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Основной компонент Buddy Flow Preview
const BuddyFlowPreview = () => {
  const [selectedStep, setSelectedStep] = useState(null);
  const [viewMode, setViewMode] = useState('overview'); // 'overview' | 'details'

  // Демо данные
  const flowData = {
    id: 1,
    title: "Онбординг нового дизайнера",
    description: "Комплексный курс введения в работу дизайн-команды компании",
    is_active: true,
    created_at: "2024-01-15",
    total_steps: 6,
    estimated_time_hours: 8
  };

  const stepsData = [
    {
      id: 1,
      title: "Знакомство с дизайн-системой",
      description: "Изучите основные принципы и компоненты нашей дизайн-системы",
      step_type: "article",
      order: 1,
      is_required: true,
      estimated_time_minutes: 45,
      article: {
        title: "Дизайн-система компании",
        content: "<h2>Основы дизайн-системы</h2><p>Наша дизайн-система построена на принципах атомарного дизайна...</p>"
      }
    },
    {
      id: 2,
      title: "Поиск в Figma файлах",
      description: "Найдите секретное кодовое слово в файлах дизайн-системы",
      step_type: "task",
      order: 2,
      is_required: true,
      estimated_time_minutes: 30,
      task: {
        title: "Навигация по Figma",
        description: "Освойте структуру наших Figma файлов",
        instruction: "Откройте главный файл дизайн-системы и найдите скрытое слово в секции Colors"
      }
    },
    {
      id: 3,
      title: "Тест по UI принципам",
      description: "Проверьте понимание основных принципов пользовательского интерфейса",
      step_type: "quiz",
      order: 3,
      is_required: true,
      estimated_time_minutes: 20,
      quiz: {
        title: "UI/UX Основы",
        description: "Тест на знание базовых принципов дизайна",
        passing_score_percentage: 80,
        questions: [
          { id: 1, question: "Что такое принцип близости в дизайне?" },
          { id: 2, question: "Какой размер минимальной области касания?" }
        ]
      }
    },
    {
      id: 4,
      title: "Работа с компонентами",
      description: "Изучите как правильно использовать готовые компоненты",
      step_type: "article",
      order: 4,
      is_required: true,
      estimated_time_minutes: 35,
      article: {
        title: "Библиотека компонентов",
        content: "<h2>Использование компонентов</h2><p>Компоненты позволяют создавать консистентный интерфейс...</p>"
      }
    },
    {
      id: 5,
      title: "Создание макета",
      description: "Примените полученные знания для создания простого макета",
      step_type: "task",
      order: 5,
      is_required: true,
      estimated_time_minutes: 60,
      task: {
        title: "Первый макет",
        description: "Создайте макет страницы входа используя нашу дизайн-систему",
        instruction: "Используйте только компоненты из библиотеки для создания страницы логина"
      }
    },
    {
      id: 6,
      title: "Финальная проверка",
      description: "Итоговый тест по всем изученным материалам",
      step_type: "quiz",
      order: 6,
      is_required: true,
      estimated_time_minutes: 25,
      quiz: {
        title: "Итоговый тест",
        description: "Проверка всех полученных знаний",
        passing_score_percentage: 75
      }
    }
  ];

  // Демо прогресс пользователей
  const getUserProgress = (stepId) => [
    { user: { name: "Анна Иванова", position: "Junior Designer" }, status: "completed" },
    { user: { name: "Петр Сидоров", position: "UX Designer" }, status: "in_progress" },
    { user: { name: "Мария Козлова", position: "UI Designer" }, status: "not_started" }
  ];

  const getStepProgress = (stepId) => {
    const users = getUserProgress(stepId);
    return {
      completed: users.filter(u => u.status === 'completed').length,
      total: users.length
    };
  };

  const handleStepSelect = (step) => {
    setSelectedStep(step);
    setViewMode('details');
  };

  const handleBackToOverview = () => {
    setSelectedStep(null);
    setViewMode('overview');
  };

  if (viewMode === 'details' && selectedStep) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-4xl mx-auto">
          <StepDetailView 
            step={selectedStep}
            onBack={handleBackToOverview}
            userProgress={getUserProgress(selectedStep.id)}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Eye className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">{flowData.title}</h1>
                  <p className="text-gray-600">Превью потока обучения</p>
                </div>
              </div>
              
              <p className="text-gray-700 max-w-2xl">{flowData.description}</p>
            </div>
            
            <div className="flex gap-2">
              <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium flex items-center gap-2 transition-colors">
                <Play className="w-4 h-4" />
                Назначить поток
              </button>
              <button className="px-4 py-2 border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-lg font-medium flex items-center gap-2 transition-colors">
                <Settings className="w-4 h-4" />
                Настройки
              </button>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-4 gap-4 mt-6">
            <div className="bg-blue-50 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-blue-600">{flowData.total_steps}</div>
              <div className="text-sm text-blue-700">Этапов</div>
            </div>
            <div className="bg-green-50 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-green-600">{flowData.estimated_time_hours}ч</div>
              <div className="text-sm text-green-700">Время</div>
            </div>
            <div className="bg-purple-50 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-purple-600">12</div>
              <div className="text-sm text-purple-700">Пользователей</div>
            </div>
            <div className="bg-orange-50 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-orange-600">67%</div>
              <div className="text-sm text-orange-700">Завершаемость</div>
            </div>
          </div>
        </div>
      </div>

      {/* Steps Grid */}
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Этапы потока</h2>
          <p className="text-gray-600">Нажмите на любой этап для подробного просмотра</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {stepsData.map((step, index) => (
            <StepPreview
              key={step.id}
              step={step}
              stepNumber={index + 1}
              onViewDetails={handleStepSelect}
              isSelected={selectedStep?.id === step.id}
              progress={getStepProgress(step.id)}
            />
          ))}
        </div>

        {/* Flow Timeline */}
        <div className="mt-12 bg-white rounded-xl shadow-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
            <Calendar className="w-5 h-5" />
            Порядок прохождения
          </h3>
          
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200"></div>
            
            <div className="space-y-6">
              {stepsData.map((step, index) => (
                <div key={step.id} className="relative flex items-center gap-4">
                  {/* Timeline dot */}
                  <div className={`relative z-10 w-12 h-12 rounded-full border-4 border-white shadow-lg flex items-center justify-center ${
                    step.step_type === 'article' ? 'bg-blue-500' :
                    step.step_type === 'task' ? 'bg-purple-500' :
                    step.step_type === 'quiz' ? 'bg-emerald-500' : 'bg-gray-500'
                  }`}>
                    <span className="text-white font-bold text-sm">{index + 1}</span>
                  </div>
                  
                  <div className="flex-1 bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-gray-900">{step.title}</h4>
                        <p className="text-sm text-gray-600">{step.description}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-gray-700">{step.estimated_time_minutes}м</div>
                        <div className="text-xs text-gray-500 capitalize">{step.step_type}</div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BuddyFlowPreview;