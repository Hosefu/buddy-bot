import React, { useState } from 'react';
import { 
  BookOpen, 
  Search, 
  HelpCircle, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Trophy, 
  Target,
  Lightbulb,
  ChevronRight,
  ChevronDown,
  PlayCircle
} from 'lucide-react';

// Атомарный компонент Article
const ArticleComponent = ({ article, onComplete, isCompleted = false }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-6 text-white">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-white/20 rounded-lg">
            <BookOpen className="w-6 h-6" />
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-bold">{article.title}</h3>
            <p className="text-blue-100 text-sm">Изучите материал</p>
          </div>
          {isCompleted && (
            <div className="p-2 bg-green-500 rounded-full">
              <CheckCircle className="w-6 h-6" />
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        <div className="prose prose-lg max-w-none">
          <div 
            className={`markdown-content transition-all duration-300 ${
              isExpanded ? 'max-h-none' : 'max-h-64 overflow-hidden'
            }`}
            dangerouslySetInnerHTML={{ __html: article.content }}
          />
        </div>
        
        {!isExpanded && (
          <div className="mt-4 text-center">
            <button 
              onClick={() => setIsExpanded(true)}
              className="flex items-center gap-2 mx-auto px-4 py-2 text-blue-600 hover:text-blue-700 font-medium"
            >
              Читать полностью <ChevronDown className="w-4 h-4" />
            </button>
          </div>
        )}

        {isExpanded && !isCompleted && (
          <div className="mt-6 flex justify-center">
            <button
              onClick={onComplete}
              className="px-8 py-3 bg-green-500 hover:bg-green-600 text-white rounded-xl font-semibold transition-colors flex items-center gap-2"
            >
              <CheckCircle className="w-5 h-5" />
              Отметить как прочитано
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// Атомарный компонент Task  
const TaskComponent = ({ task, onSubmit, isCompleted = false }) => {
  const [answer, setAnswer] = useState('');
  const [showHint, setShowHint] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onSubmit(answer);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-500 to-purple-600 p-6 text-white">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-white/20 rounded-lg">
            <Target className="w-6 h-6" />
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-bold">{task.title}</h3>
            <p className="text-purple-100 text-sm">Найдите кодовое слово</p>
          </div>
          {isCompleted && (
            <div className="p-2 bg-green-500 rounded-full">
              <CheckCircle className="w-6 h-6" />
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        <div className="space-y-6">
          <div>
            <h4 className="font-semibold text-gray-900 mb-2">Описание задания:</h4>
            <p className="text-gray-700 leading-relaxed">{task.description}</p>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
            <h4 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
              <Search className="w-5 h-5" />
              Инструкция:
            </h4>
            <p className="text-blue-800">{task.instruction}</p>
          </div>

          {task.hint && (
            <div className="space-y-2">
              <button
                onClick={() => setShowHint(!showHint)}
                className="flex items-center gap-2 text-amber-600 hover:text-amber-700 font-medium"
              >
                <Lightbulb className="w-4 h-4" />
                {showHint ? 'Скрыть подсказку' : 'Показать подсказку'}
              </button>
              
              {showHint && (
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                  <p className="text-amber-800">{task.hint}</p>
                </div>
              )}
            </div>
          )}

          {!isCompleted && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Введите кодовое слово:
                </label>
                <input
                  type="text"
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  placeholder="Ваш ответ..."
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && answer.trim()) {
                      handleSubmit(e);
                    }
                  }}
                />
              </div>
              
              <button
                onClick={handleSubmit}
                disabled={isSubmitting || !answer.trim()}
                className="w-full px-6 py-3 bg-purple-500 hover:bg-purple-600 disabled:bg-gray-300 text-white rounded-xl font-semibold transition-colors flex items-center justify-center gap-2"
              >
                {isSubmitting ? (
                  <>Проверяем...</>
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5" />
                    Проверить ответ
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Атомарный компонент Quiz
const QuizComponent = ({ quiz, questions, onComplete, isCompleted = false }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [score, setScore] = useState(null);

  const handleAnswerSelect = (questionId, answerId) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answerId
    }));
  };

  const handleSubmit = () => {
    // Подсчет результатов
    let correct = 0;
    questions.forEach(question => {
      const selectedAnswer = question.answers.find(
        answer => answer.id === answers[question.id]
      );
      if (selectedAnswer?.is_correct) {
        correct++;
      }
    });

    const finalScore = Math.round((correct / questions.length) * 100);
    setScore(finalScore);
    setShowResults(true);
    
    if (finalScore >= quiz.passing_score_percentage) {
      onComplete?.(finalScore);
    }
  };

  const canProceed = currentQuestion < questions.length - 1;
  const isLastQuestion = currentQuestion === questions.length - 1;
  const hasAnsweredCurrent = answers[questions[currentQuestion]?.id];

  if (showResults) {
    const isPassed = score >= quiz.passing_score_percentage;
    
    return (
      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
        <div className={`p-6 text-white ${isPassed ? 'bg-green-500' : 'bg-red-500'}`}>
          <div className="text-center">
            {isPassed ? (
              <Trophy className="w-16 h-16 mx-auto mb-4" />
            ) : (
              <XCircle className="w-16 h-16 mx-auto mb-4" />
            )}
            <h3 className="text-2xl font-bold">
              {isPassed ? 'Поздравляем!' : 'Попробуйте еще раз'}
            </h3>
            <p className="text-lg mt-2">Ваш результат: {score}%</p>
            <p className="text-sm opacity-90">
              Для прохождения нужно {quiz.passing_score_percentage}%
            </p>
          </div>
        </div>
        
        <div className="p-6">
          <div className="space-y-4">
            {questions.map((question, idx) => {
              const selectedAnswer = question.answers.find(
                answer => answer.id === answers[question.id]
              );
              const correctAnswer = question.answers.find(answer => answer.is_correct);
              const isCorrect = selectedAnswer?.is_correct;
              
              return (
                <div key={question.id} className="border border-gray-200 rounded-xl p-4">
                  <div className="flex items-start gap-3">
                    <div className={`p-1 rounded-full ${isCorrect ? 'bg-green-100' : 'bg-red-100'}`}>
                      {isCorrect ? (
                        <CheckCircle className="w-4 h-4 text-green-600" />
                      ) : (
                        <XCircle className="w-4 h-4 text-red-600" />
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{question.question}</p>
                      <p className="text-sm text-gray-600 mt-1">
                        Ваш ответ: <span className={isCorrect ? 'text-green-600' : 'text-red-600'}>
                          {selectedAnswer?.answer_text}
                        </span>
                      </p>
                      {!isCorrect && (
                        <p className="text-sm text-green-600 mt-1">
                          Правильный ответ: {correctAnswer?.answer_text}
                        </p>
                      )}
                      {selectedAnswer?.explanation && (
                        <p className="text-sm text-gray-500 mt-2">{selectedAnswer.explanation}</p>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  }

  const question = questions[currentQuestion];

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-500 to-emerald-600 p-6 text-white">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-white/20 rounded-lg">
            <HelpCircle className="w-6 h-6" />
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-bold">{quiz.title}</h3>
            <p className="text-emerald-100 text-sm">
              Вопрос {currentQuestion + 1} из {questions.length}
            </p>
          </div>
          {isCompleted && (
            <div className="p-2 bg-green-500 rounded-full">
              <CheckCircle className="w-6 h-6" />
            </div>
          )}
        </div>
        
        {/* Progress bar */}
        <div className="mt-4 bg-white/20 rounded-full h-2">
          <div 
            className="bg-white rounded-full h-2 transition-all duration-300"
            style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        <div className="space-y-6">
          <div>
            <h4 className="text-lg font-semibold text-gray-900 mb-4">
              {question.question}
            </h4>
            
            <div className="space-y-3">
              {question.answers.map((answer) => (
                <label
                  key={answer.id}
                  className={`flex items-center p-4 border-2 rounded-xl cursor-pointer transition-all ${
                    answers[question.id] === answer.id
                      ? 'border-emerald-500 bg-emerald-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    type="radio"
                    name={`question-${question.id}`}
                    value={answer.id}
                    checked={answers[question.id] === answer.id}
                    onChange={() => handleAnswerSelect(question.id, answer.id)}
                    className="sr-only"
                  />
                  <div className={`w-5 h-5 rounded-full border-2 mr-3 flex items-center justify-center ${
                    answers[question.id] === answer.id
                      ? 'border-emerald-500 bg-emerald-500'
                      : 'border-gray-300'
                  }`}>
                    {answers[question.id] === answer.id && (
                      <div className="w-2 h-2 bg-white rounded-full" />
                    )}
                  </div>
                  <span className="text-gray-700">{answer.answer_text}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="flex justify-between items-center pt-4">
            <button
              onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
              disabled={currentQuestion === 0}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 disabled:text-gray-400 font-medium"
            >
              ← Назад
            </button>

            {canProceed ? (
              <button
                onClick={() => setCurrentQuestion(currentQuestion + 1)}
                disabled={!hasAnsweredCurrent}
                className="px-6 py-3 bg-emerald-500 hover:bg-emerald-600 disabled:bg-gray-300 text-white rounded-xl font-semibold transition-colors flex items-center gap-2"
              >
                Далее <ChevronRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={!hasAnsweredCurrent}
                className="px-6 py-3 bg-emerald-500 hover:bg-emerald-600 disabled:bg-gray-300 text-white rounded-xl font-semibold transition-colors flex items-center gap-2"
              >
                <Trophy className="w-5 h-5" />
                Завершить тест
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Demo компонент для показа всех атомарных компонентов
const FlowComponentsDemo = () => {
  const [completedComponents, setCompletedComponents] = useState(new Set());

  const sampleArticle = {
    id: 1,
    title: "Основы работы с дизайн-системой",
    content: `
      <h2>Что такое дизайн-система?</h2>
      <p>Дизайн-система — это набор переиспользуемых компонентов, руководящих принципов и стандартов, которые помогают создавать последовательный пользовательский опыт.</p>
      
      <h3>Основные компоненты:</h3>
      <ul>
        <li><strong>UI Kit</strong> — библиотека компонентов</li>
        <li><strong>Style Guide</strong> — руководство по стилю</li>
        <li><strong>Pattern Library</strong> — библиотека паттернов</li>
      </ul>
      
      <p>Использование дизайн-системы ускоряет разработку и обеспечивает консистентность интерфейса.</p>
    `
  };

  const sampleTask = {
    id: 2,
    title: "Найти секретное слово в Figma",
    description: "В файле дизайн-системы спрятано кодовое слово. Найдите его и введите ниже.",
    instruction: "Откройте файл 'Design System v2.0' в Figma, перейдите на страницу 'Colors' и найдите скрытый текст за цветовой палитрой.",
    hint: "Попробуйте выделить весь контент на странице Colors — там может быть скрытый белый текст!"
  };

  const sampleQuiz = {
    id: 3,
    title: "Проверка знаний UX/UI",
    description: "Тест на понимание основных принципов UX/UI дизайна",
    passing_score_percentage: 70
  };

  const sampleQuestions = [
    {
      id: 1,
      question: "Что означает принцип 'Mobile First' в веб-дизайне?",
      answers: [
        { id: 1, answer_text: "Сначала разрабатывать для мобильных устройств", is_correct: true, explanation: "Правильно! Mobile First означает начинать дизайн с мобильной версии." },
        { id: 2, answer_text: "Мобильные устройства важнее десктопа", is_correct: false, explanation: "Не совсем. Это подход к разработке, а не приоритизация." },
        { id: 3, answer_text: "Использовать только мобильные технологии", is_correct: false, explanation: "Нет, это про последовательность разработки интерфейса." }
      ]
    },
    {
      id: 2,
      question: "Какой принцип UX описывает 'не заставляйте пользователя думать'?",
      answers: [
        { id: 4, answer_text: "Принцип простоты", is_correct: false, explanation: "Близко, но есть более точное определение." },
        { id: 5, answer_text: "Принцип интуитивности", is_correct: true, explanation: "Верно! Интерфейс должен быть интуитивно понятным." },
        { id: 6, answer_text: "Принцип минимализма", is_correct: false, explanation: "Минимализм — это про визуальную простоту." }
      ]
    }
  ];

  const handleComplete = (componentId) => {
    setCompletedComponents(prev => new Set([...prev, componentId]));
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 space-y-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Атомарные компоненты Flow
          </h1>
          <p className="text-gray-600">
            Основные блоки для построения потоков обучения
          </p>
        </div>

        {/* Article Component */}
        <div className="space-y-3">
          <h2 className="text-xl font-semibold text-gray-800 flex items-center gap-2">
            <BookOpen className="w-5 h-5" />
            Article Component
          </h2>
          <ArticleComponent 
            article={sampleArticle}
            onComplete={() => handleComplete('article')}
            isCompleted={completedComponents.has('article')}
          />
        </div>

        {/* Task Component */}
        <div className="space-y-3">
          <h2 className="text-xl font-semibold text-gray-800 flex items-center gap-2">
            <Target className="w-5 h-5" />
            Task Component
          </h2>
          <TaskComponent 
            task={sampleTask}
            onSubmit={(answer) => {
              console.log('Task answer:', answer);
              handleComplete('task');
            }}
            isCompleted={completedComponents.has('task')}
          />
        </div>

        {/* Quiz Component */}
        <div className="space-y-3">
          <h2 className="text-xl font-semibold text-gray-800 flex items-center gap-2">
            <HelpCircle className="w-5 h-5" />
            Quiz Component
          </h2>
          <QuizComponent 
            quiz={sampleQuiz}
            questions={sampleQuestions}
            onComplete={(score) => {
              console.log('Quiz completed with score:', score);
              handleComplete('quiz');
            }}
            isCompleted={completedComponents.has('quiz')}
          />
        </div>
      </div>
    </div>
  );
};

export default FlowComponentsDemo;