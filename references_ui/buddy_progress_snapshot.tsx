import React, { useState } from 'react';
import { 
  User, 
  BookOpen, 
  Target, 
  HelpCircle, 
  Clock, 
  CheckCircle, 
  XCircle,
  Pause,
  Play,
  Calendar,
  TrendingUp,
  AlertCircle,
  Award,
  Eye,
  MessageCircle,
  Activity,
  BarChart3,
  Timer,
  ChevronDown,
  ChevronRight,
  Zap,
  Coffee,
  Brain
} from 'lucide-react';

// Компонент для отображения статуса этапа
const StepStatus = ({ step, progress, onViewSnapshot }) => {
  const [showDetails, setShowDetails] = useState(false);

  const getStepIcon = (type) => {
    switch (type) {
      case 'article': return <BookOpen className="w-4 h-4" />;
      case 'task': return <Target className="w-4 h-4" />;
      case 'quiz': return <HelpCircle className="w-4 h-4" />;
      default: return <BookOpen className="w-4 h-4" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'green';
      case 'in_progress': return 'blue';
      case 'locked': return 'gray';
      case 'not_started': return 'gray';
      default: return 'gray';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-5 h-5" />;
      case 'in_progress': return <Play className="w-5 h-5" />;
      case 'locked': return <XCircle className="w-5 h-5" />;
      default: return <Pause className="w-5 h-5" />;
    }
  };

  const color = getStatusColor(progress.status);

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
      <div className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3 flex-1">
            <div className={`p-2 bg-${color}-100 rounded-lg`}>
              {getStepIcon(step.step_type)}
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-semibold text-gray-900 text-sm">{step.title}</h3>
                <span className={`text-xs font-medium bg-${color}-100 text-${color}-800 px-2 py-1 rounded-full`}>
                  {progress.status === 'completed' ? 'Завершено' :
                   progress.status === 'in_progress' ? 'В процессе' :
                   progress.status === 'locked' ? 'Заблокировано' : 'Не начато'}
                </span>
              </div>
              
              <p className="text-xs text-gray-600 mb-2">{step.description}</p>
              
              {/* Timeline */}
              <div className="flex items-center gap-4 text-xs text-gray-500">
                {progress.started_at && (
                  <div className="flex items-center gap-1">
                    <Play className="w-3 h-3" />
                    Начато: {new Date(progress.started_at).toLocaleDateString()}
                  </div>
                )}
                {progress.completed_at && (
                  <div className="flex items-center gap-1">
                    <CheckCircle className="w-3 h-3" />
                    Завершено: {new Date(progress.completed_at).toLocaleDateString()}
                  </div>
                )}
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <div className={`p-2 text-${color}-600`}>
              {getStatusIcon(progress.status)}
            </div>
            
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="p-1 text-gray-400 hover:text-gray-600"
            >
              {showDetails ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </button>
          </div>
        </div>
        
        {/* Details */}
        {showDetails && (
          <div className="mt-4 pt-4 border-t border-gray-100 space-y-3">
            {/* Step specific details */}
            {step.step_type === 'article' && progress.article_read_at && (
              <div className="bg-blue-50 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-blue-800">Статья прочитана</span>
                  <span className="text-xs text-blue-600">
                    {new Date(progress.article_read_at).toLocaleString()}
                  </span>
                </div>
              </div>
            )}
            
            {step.step_type === 'task' && progress.task_completed_at && (
              <div className="bg-purple-50 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-purple-800">Задание выполнено</span>
                  <span className="text-xs text-purple-600">
                    {new Date(progress.task_completed_at).toLocaleString()}
                  </span>
                </div>
                {progress.task_attempts && (
                  <div className="text-xs text-purple-600 mt-1">
                    Попыток: {progress.task_attempts}
                  </div>
                )}
              </div>
            )}
            
            {step.step_type === 'quiz' && progress.quiz_completed_at && (
              <div className="bg-emerald-50 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-emerald-800">Квиз пройден</span>
                  <span className="text-xs text-emerald-600">
                    {new Date(progress.quiz_completed_at).toLocaleString()}
                  </span>
                </div>
                {progress.quiz_score !== null && (
                  <div className="text-sm text-emerald-700 mt-1">
                    Результат: {progress.quiz_score}% ({progress.quiz_correct_answers}/{progress.quiz_total_questions})
                  </div>
                )}
              </div>
            )}
            
            {/* Content Snapshot */}
            {progress.content_snapshot && (
              <button
                onClick={() => onViewSnapshot(step, progress)}
                className="w-full flex items-center justify-center gap-2 p-2 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors text-sm text-gray-700"
              >
                <Eye className="w-4 h-4" />
                Посмотреть снапшот контента
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// Компонент для детального снапшота контента
const ContentSnapshot = ({ step, progress, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div className="bg-gray-900 text-white p-4 flex items-center justify-between">
          <div>
            <h3 className="font-semibold">Снапшот контента</h3>
            <p className="text-sm text-gray-300">{step.title}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
          >
            <XCircle className="w-5 h-5" />
          </button>
        </div>
        
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
          <div className="space-y-4">
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-sm text-yellow-800">
                Это снапшот контента на момент прохождения этапа пользователем.
                Он сохраняет оригинальную версию контента.
              </p>
            </div>
            
            <div className="prose prose-sm max-w-none">
              <div dangerouslySetInnerHTML={{ __html: progress.content_snapshot }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Основной компонент Progress Snapshot
const BuddyProgressSnapshot = () => {
  const [selectedSnapshot, setSelectedSnapshot] = useState(null);
  const [timeFilter, setTimeFilter] = useState('all'); // 'all', 'week', 'month'

  // Демо данные пользователя
  const userData = {
    id: 1,
    name: "Анна Иванова",
    email: "anna.ivanova@company.com",
    position: "Junior UX Designer",
    department: "Design",
    hire_date: "2024-01-15",
    avatar: null
  };

  // Демо данных о потоке
  const userFlowData = {
    id: 1,
    flow: {
      title: "Онбординг нового дизайнера",
      description: "Комплексный курс введения в работу дизайн-команды"
    },
    status: "in_progress",
    started_at: "2024-01-16T09:00:00Z",
    expected_completion_date: "2024-01-30",
    current_step: 3,
    buddy_name: "Петр Смирнов"
  };

  // Демо прогресса по этапам
  const progressData = [
    {
      step: {
        id: 1,
        title: "Знакомство с дизайн-системой",
        description: "Изучите основные принципы и компоненты",
        step_type: "article",
        order: 1
      },
      progress: {
        status: "completed",
        started_at: "2024-01-16T09:30:00Z",
        completed_at: "2024-01-16T10:15:00Z",
        article_read_at: "2024-01-16T10:15:00Z",
        content_snapshot: "<h2>Дизайн-система компании</h2><p>Наша дизайн-система построена на принципах атомарного дизайна...</p>"
      }
    },
    {
      step: {
        id: 2,
        title: "Поиск в Figma файлах",
        description: "Найдите секретное кодовое слово",
        step_type: "task",
        order: 2
      },
      progress: {
        status: "completed",
        started_at: "2024-01-16T10:30:00Z",
        completed_at: "2024-01-16T11:45:00Z",
        task_completed_at: "2024-01-16T11:45:00Z",
        task_attempts: 2,
        content_snapshot: "<h3>Инструкция</h3><p>Откройте файл 'Design System v2.0' в Figma...</p>"
      }
    },
    {
      step: {
        id: 3,
        title: "Тест по UI принципам",
        description: "Проверьте понимание основных принципов",
        step_type: "quiz",
        order: 3
      },
      progress: {
        status: "in_progress",
        started_at: "2024-01-17T09:00:00Z",
        quiz_score: null,
        quiz_correct_answers: null,
        quiz_total_questions: 5
      }
    },
    {
      step: {
        id: 4,
        title: "Работа с компонентами",
        description: "Изучите как правильно использовать компоненты",
        step_type: "article",
        order: 4
      },
      progress: {
        status: "locked"
      }
    }
  ];

  // Подсчет статистики
  const totalSteps = progressData.length;
  const completedSteps = progressData.filter(p => p.progress.status === 'completed').length;
  const completionPercentage = Math.round((completedSteps / totalSteps) * 100);
  
  const totalTimeSpent = progressData
    .filter(p => p.progress.started_at && p.progress.completed_at)
    .reduce((total, p) => {
      const start = new Date(p.progress.started_at);
      const end = new Date(p.progress.completed_at);
      return total + (end - start);
    }, 0);
  
  const averageTimePerStep = totalTimeSpent / completedSteps / (1000 * 60); // в минутах

  const handleViewSnapshot = (step, progress) => {
    setSelectedSnapshot({ step, progress });
  };

  const getActivityLevel = () => {
    const recentActivity = progressData.filter(p => {
      if (!p.progress.completed_at) return false;
      const completed = new Date(p.progress.completed_at);
      const weekAgo = new Date();
      weekAgo.setDate(weekAgo.getDate() - 7);
      return completed > weekAgo;
    }).length;
    
    if (recentActivity >= 3) return { level: 'high', color: 'green', text: 'Высокая' };
    if (recentActivity >= 1) return { level: 'medium', color: 'yellow', text: 'Средняя' };
    return { level: 'low', color: 'red', text: 'Низкая' };
  };

  const activity = getActivityLevel();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="flex items-start gap-6">
            {/* User Avatar */}
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-white text-2xl font-bold">
              {userData.name.charAt(0)}
            </div>
            
            {/* User Info */}
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-2xl font-bold text-gray-900">{userData.name}</h1>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  userFlowData.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                  userFlowData.status === 'completed' ? 'bg-green-100 text-green-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {userFlowData.status === 'in_progress' ? 'В процессе' :
                   userFlowData.status === 'completed' ? 'Завершен' : 'Не начат'}
                </span>
              </div>
              
              <div className="text-gray-600 space-y-1">
                <p className="font-medium">{userData.position} • {userData.department}</p>
                <p className="text-sm">Дата найма: {new Date(userData.hire_date).toLocaleDateString()}</p>
                <p className="text-sm">Поток: <span className="font-medium">{userFlowData.flow.title}</span></p>
              </div>
            </div>
            
            {/* Actions */}
            <div className="flex gap-2">
              <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium flex items-center gap-2 transition-colors">
                <MessageCircle className="w-4 h-4" />
                Написать
              </button>
              <button className="px-4 py-2 border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-lg font-medium transition-colors">
                Настройки
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Dashboard */}
      <div className="max-w-6xl mx-auto px-4 py-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <BarChart3 className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">{completionPercentage}%</div>
                <div className="text-sm text-gray-600">Прогресс</div>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">{completedSteps}/{totalSteps}</div>
                <div className="text-sm text-gray-600">Этапов</div>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Timer className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">{Math.round(averageTimePerStep)}м</div>
                <div className="text-sm text-gray-600">Среднее время</div>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-200">
            <div className="flex items-center gap-3">
              <div className={`p-2 bg-${activity.color}-100 rounded-lg`}>
                <Activity className={`w-5 h-5 text-${activity.color}-600`} />
              </div>
              <div>
                <div className={`text-2xl font-bold text-${activity.color}-600`}>{activity.text}</div>
                <div className="text-sm text-gray-600">Активность</div>
              </div>
            </div>
          </div>
        </div>

        {/* Timeline */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              Временная шкала
            </h2>
            
            <div className="flex gap-2">
              <button 
                onClick={() => setTimeFilter('all')}
                className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                  timeFilter === 'all' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                Все время
              </button>
              <button 
                onClick={() => setTimeFilter('week')}
                className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                  timeFilter === 'week' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                Неделя
              </button>
              <button 
                onClick={() => setTimeFilter('month')}
                className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                  timeFilter === 'month' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                Месяц
              </button>
            </div>
          </div>
          
          <div className="space-y-4">
            {progressData
              .filter(p => p.progress.started_at || p.progress.completed_at)
              .map(({ step, progress }) => (
                <div key={step.id} className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
                  <div className={`w-3 h-3 rounded-full ${
                    progress.status === 'completed' ? 'bg-green-500' :
                    progress.status === 'in_progress' ? 'bg-blue-500' : 'bg-gray-300'
                  }`} />
                  
                  <div className="flex-1">
                    <div className="font-medium text-gray-900 text-sm">{step.title}</div>
                    <div className="text-xs text-gray-600">
                      {progress.started_at && (
                        <>Начато: {new Date(progress.started_at).toLocaleString()}</>
                      )}
                      {progress.completed_at && (
                        <> • Завершено: {new Date(progress.completed_at).toLocaleString()}</>
                      )}
                    </div>
                  </div>
                  
                  <div className="text-xs text-gray-500 capitalize">{step.step_type}</div>
                </div>
              ))}
          </div>
        </div>

        {/* Steps Progress */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Детальный прогресс по этапам</h2>
            <div className="text-sm text-gray-600">
              Текущий этап: {userFlowData.current_step} из {totalSteps}
            </div>
          </div>
          
          <div className="space-y-4">
            {progressData.map(({ step, progress }) => (
              <StepStatus
                key={step.id}
                step={step}
                progress={progress}
                onViewSnapshot={handleViewSnapshot}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Content Snapshot Modal */}
      {selectedSnapshot && (
        <ContentSnapshot
          step={selectedSnapshot.step}
          progress={selectedSnapshot.progress}
          onClose={() => setSelectedSnapshot(null)}
        />
      )}
    </div>
  );
};

export default BuddyProgressSnapshot;