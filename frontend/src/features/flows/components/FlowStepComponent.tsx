import React, { useState } from 'react';
import { Article, Task, Quiz } from '../types';
import { BookOpenIcon, PencilSquareIcon, QuestionMarkCircleIcon } from '@heroicons/react/24/outline';
import { useGetArticleDetailsQuery } from '../flowApi';
import 'highlight.js/styles/github.css';
import hljs from 'highlight.js';
import { Marked } from 'marked';
import { markedHighlight } from "marked-highlight";

interface ArticleViewProps {
  article: Article;
}

interface TaskViewProps {
  task: Task;
  isPreview?: boolean;
}

interface QuizViewProps {
  quiz: Quiz;
  isPreview?: boolean;
}

interface FlowStepComponentProps {
  step: {
    id: number;
    title: string;
    description: string;
    article: Article;
    task: Task;
    quiz: Quiz;
  };
  isPreview?: boolean;
}

const ArticleView: React.FC<ArticleViewProps> = ({ article }) => {
  const { data: fullArticle, isLoading, error } = useGetArticleDetailsQuery(article.slug);

  if (isLoading) return <div className="p-6">Загрузка статьи...</div>;
  if (error) return <div className="p-6 text-red-500">Не удалось загрузить статью.</div>;

  const markedExtended = new Marked(
    markedHighlight({
      langPrefix: 'hljs language-',
      highlight(code: string, lang: string) {
        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
        return hljs.highlight(code, { language }).value;
      }
    })
  );

  return (
    <div className="p-6 bg-white rounded-lg shadow-sm border">
      <h3 className="text-2xl font-bold mb-4">{fullArticle?.title || article.title}</h3>
      <div className="mb-4">
        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800">
          {article.difficulty_level === 'beginner' ? 'Начальный уровень' : 
           article.difficulty_level === 'intermediate' ? 'Средний уровень' : 'Продвинутый уровень'}
        </span>
        <span className="ml-4 text-gray-600">
          Время чтения: {article.reading_time_minutes} мин.
        </span>
      </div>
      {fullArticle?.content ? (
        <div 
          className="prose max-w-none" 
          dangerouslySetInnerHTML={{ __html: markedExtended.parse(fullArticle.content) as string }}
        />
      ) : (
        <p className="text-gray-500">Содержимое статьи отсутствует.</p>
      )}
    </div>
  );
};

const TaskView: React.FC<TaskViewProps> = ({ task, isPreview }) => {
  const [answer, setAnswer] = useState('');

  return (
    <div className="p-6 bg-white rounded-lg shadow-sm border">
      <h3 className="text-2xl font-bold mb-4">{task.title}</h3>
      <div className="prose max-w-none mb-6">
        <p className="text-gray-800">{task.description}</p>
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 my-4">
          <p className="text-yellow-800">
            <strong>Задание:</strong> {task.instruction}
          </p>
          {task.hint && (
            <p className="text-yellow-600 mt-2">
              <strong>Подсказка:</strong> {task.hint}
            </p>
          )}
        </div>
      </div>
      {!isPreview && (
        <div className="mt-6">
          <div className="mb-4">
            <label htmlFor="answer" className="block text-sm font-medium text-gray-700 mb-2">
              Ваш ответ:
            </label>
            <input
              id="answer"
              type="text"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Введите ответ..."
            />
          </div>
        </div>
      )}
    </div>
  );
};

const QuizView: React.FC<QuizViewProps> = ({ quiz, isPreview }) => {
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number>>({});

  return (
    <div className="p-6 bg-white rounded-lg shadow-sm border">
      <h3 className="text-2xl font-bold mb-4">{quiz.title}</h3>
      {quiz.description && <p className="text-gray-600 mb-6">{quiz.description}</p>}
      <div className="space-y-8">
        {quiz.questions.map((question, index) => (
          <div key={question.id} className="border-b pb-6 last:border-b-0">
            <p className="font-medium text-lg mb-4">
              {index + 1}. {question.question}
            </p>
            <div className="space-y-3">
              {question.answers.map((answer) => (
                <label
                  key={answer.id}
                  className="flex items-start p-3 rounded-lg hover:bg-gray-50 cursor-pointer"
                >
                  <input
                    type="radio"
                    name={`question-${question.id}`}
                    value={answer.id}
                    checked={selectedAnswers[question.id] === answer.id}
                    onChange={() => {
                      setSelectedAnswers({
                        ...selectedAnswers,
                        [question.id]: answer.id,
                      });
                    }}
                    className="mt-1"
                    disabled={isPreview}
                  />
                  <span className="ml-3">{answer.answer_text}</span>
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export const FlowStepComponent: React.FC<FlowStepComponentProps> = ({ step, isPreview }) => {
  const handleSubmit = () => {
    // Тут будет логика отправки ответов на сервер
    alert('Этап отправлен на проверку!');
  };

  return (
    <div className="space-y-10">
      {step.article && (
        <section>
          <div className="flex items-center mb-4">
            <BookOpenIcon className="h-8 w-8 text-gray-500 mr-3" />
            <h2 className="text-2xl font-bold text-gray-800">Материал для изучения</h2>
          </div>
          <ArticleView article={step.article} />
        </section>
      )}
      
      {step.task && (
        <section>
          <div className="flex items-center mb-4">
            <PencilSquareIcon className="h-8 w-8 text-gray-500 mr-3" />
            <h2 className="text-2xl font-bold text-gray-800">Практическое задание</h2>
          </div>
          <TaskView task={step.task} isPreview={isPreview} />
        </section>
      )}

      {step.quiz && (
        <section>
          <div className="flex items-center mb-4">
            <QuestionMarkCircleIcon className="h-8 w-8 text-gray-500 mr-3" />
            <h2 className="text-2xl font-bold text-gray-800">Проверка знаний</h2>
          </div>
          <QuizView quiz={step.quiz} isPreview={isPreview} />
        </section>
      )}

      {!isPreview && (
        <div className="mt-12 pt-6 border-t">
          <button
            onClick={handleSubmit}
            className="w-full px-6 py-4 bg-blue-600 text-white font-bold text-xl rounded-lg hover:bg-blue-700 transition-colors shadow-lg"
          >
            Завершить и отправить на проверку
          </button>
        </div>
      )}
    </div>
  );
}; 