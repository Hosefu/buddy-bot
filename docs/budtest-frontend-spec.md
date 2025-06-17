# Техническое задание на разработку фронтенда системы BudTest

## 📋 Оглавление

1. [Общее описание проекта](#общее-описание-проекта)
2. [Технологический стек](#технологический-стек)
3. [Архитектура приложения](#архитектура-приложения)
4. [Функциональные требования](#функциональные-требования)
5. [UI/UX требования](#uiux-требования)
6. [Механики работы приложения](#механики-работы-приложения)
7. [Структура проекта](#структура-проекта)
8. [API интеграция](#api-интеграция)
9. [Безопасность](#безопасность)
10. [Локальная разработка](#локальная-разработка)
11. [Docker конфигурация](#docker-конфигурация)
12. [Критерии приемки](#критерии-приемки)

## 1. Общее описание проекта

### 1.1 Цель проекта

Разработать современный, интуитивно понятный фронтенд для корпоративной системы онбординга BudTest, работающий как Telegram Mini App. Система должна обеспечить геймифицированное обучение новых сотрудников с полным контролем процесса со стороны наставников и HR.

### 1.2 Ключевые особенности

- **Нативная интеграция с Telegram** - работа внутри мессенджера без установки
- **Ролевая модель** - разный функционал для пользователей, бадди и модераторов
- **Прогрессивное раскрытие контента** - этапы открываются последовательно
- **Реактивный интерфейс** - мгновенная обратная связь на действия
- **Офлайн-режим** - кеширование данных для работы без интернета

### 1.3 Целевая аудитория

1. **Новые сотрудники** - основные пользователи, проходящие онбординг
2. **Бадди (наставники)** - контролируют процесс обучения подопечных
3. **HR/Модераторы** - администрируют систему и анализируют результаты

## 2. Технологический стек

### 2.1 Основные технологии

```typescript
// Core
- React 18.3+ - UI библиотека
- TypeScript 5.5+ - типизация и безопасность кода
- Redux Toolkit 2.2+ - управление состоянием
- React Router 6.26+ - клиентская маршрутизация

// Data Management
- RTK Query - кеширование API запросов
- Redux Persist - сохранение состояния
- Axios 1.7+ - HTTP клиент (для не-RTK запросов)

// UI & Styling
- @telegram-apps/sdk-react 1.1+ - Telegram Mini App SDK
- Tailwind CSS 3.4+ - утилитарные стили
- Framer Motion 11+ - анимации
- React Hook Form 7.53+ - управление формами
- Zod 3.23+ - валидация схем

// Development
- Vite 5.4+ - сборщик
- ESLint + Prettier - линтинг и форматирование
- Vitest + React Testing Library - тестирование
- Storybook 8.3+ - документация компонентов
```

### 2.2 Обоснование выбора

- **React + TypeScript** - стандарт индустрии, большое сообщество, отличная поддержка
- **Redux Toolkit + RTK Query** - современный подход к state management с встроенным кешированием
- **Telegram SDK** - официальная библиотека для интеграции с Telegram Mini Apps
- **Tailwind CSS** - быстрая разработка, консистентный дизайн, малый размер бандла
- **Vite** - молниеносная сборка, отличный DX, нативная поддержка TypeScript

## 3. Архитектура приложения

### 3.1 Общая архитектура

```
┌─────────────────────────────────────────────────────────┐
│                   Telegram Mini App                      │
├─────────────────────────────────────────────────────────┤
│                    React Application                     │
├─────────────┬─────────────┬─────────────┬──────────────┤
│   Router    │    Redux    │  Services   │     UI       │
│             │   Store     │             │ Components   │
├─────────────┼─────────────┼─────────────┼──────────────┤
│  Protected  │   Slices    │    API      │   Atomic     │
│   Routes    │  Middleware │  Telegram   │   Design     │
│   Layouts   │   RTK Query │   Auth      │   System     │
└─────────────┴─────────────┴─────────────┴──────────────┘
```

### 3.2 Паттерны и принципы

1. **Feature-Sliced Design** - организация кода по фичам, а не по типам файлов
2. **Atomic Design** - компоненты от атомов до страниц
3. **Container/Presentational** - разделение логики и представления
4. **Composition over Inheritance** - композиция компонентов
5. **DRY (Don't Repeat Yourself)** - переиспользуемый код

### 3.3 State Management

```typescript
// Структура Redux Store
interface RootState {
  auth: AuthState;          // Авторизация и текущий пользователь
  flows: FlowsState;        // Потоки обучения
  progress: ProgressState;  // Прогресс прохождения
  ui: UIState;             // UI состояние (модалки, тосты)
  api: RTKQueryState;      // Кеш API запросов
}
```

## 4. Функциональные требования

### 4.1 Общий функционал (все роли)

#### 4.1.1 Авторизация
- Автоматическая авторизация через Telegram InitData
- Получение и обновление JWT токенов
- Автоматический refresh токенов
- Fallback на email/password для локальной разработки

#### 4.1.2 Навигация
- Адаптивное меню в зависимости от роли
- Breadcrumbs для глубокой навигации
- Back Button интеграция с Telegram
- Deep linking поддержка

### 4.2 Функционал для роли User

#### 4.2.1 Главная страница
```typescript
interface UserDashboard {
  activeFlows: UserFlow[];      // Активные потоки
  completedFlows: UserFlow[];   // Завершенные потоки
  overallProgress: number;      // Общий прогресс в %
  nextStep: FlowStep | null;    // Следующий шаг
}
```

**Требования:**
- Карточки активных потоков с прогресс-барами
- Быстрый доступ к текущему этапу
- Статистика прохождения
- Мотивационные элементы (стрики, достижения)

#### 4.2.2 Прохождение потока

**Страница потока:**
- Название и описание потока
- Список этапов с индикацией доступности
- Общий прогресс и оставшееся время
- Информация о бадди

**Типы контента:**

1. **Статьи (Article)**
   - Рендеринг Markdown с поддержкой:
     - Заголовков, списков, таблиц
     - Кода с подсветкой синтаксиса
     - Изображений и видео
     - Внутренних и внешних ссылок
   - Автоматическая отметка о прочтении при скролле до конца
   - Время чтения
   - Кнопка "Понятно" для перехода далее

2. **Задания (Task)**
   - Описание задачи
   - Поле ввода кодового слова
   - Подсказки (появляются через время)
   - Валидация в реальном времени
   - Анимация успеха/ошибки

3. **Квизы (Quiz)**
   - Прогресс-бар прохождения
   - Один вопрос на экране
   - 5 вариантов ответа с радио-кнопками
   - Немедленная обратная связь (правильно/неправильно)
   - Объяснение после выбора ответа
   - Итоговый экран с результатами

### 4.3 Функционал для роли Buddy

#### 4.3.1 Управление подопечными

**Список подопечных:**
```typescript
interface BuddyDashboard {
  activeFlows: FlowWithUser[];    // Активные потоки с юзерами
  problemUsers: User[];           // Проблемные пользователи
  recentActions: FlowAction[];    // История действий
}
```

**Карточка подопечного:**
- ФИО и фото из Telegram
- Текущий поток и этап
- Прогресс в процентах
- Время с последней активности
- Быстрые действия (пауза, продление)

#### 4.3.2 Запуск потока

**Процесс запуска:**
1. Выбор потока из списка активных
2. Выбор пользователя (с поиском)
3. Установка дедлайна
4. Назначение дополнительных бадди
5. Подтверждение и запуск

**Управление потоком:**
- Pause/Resume с указанием причины
- Продление дедлайна
- Просмотр детального прогресса
- История всех действий

### 4.4 Функционал для роли Moderator

#### 4.4.1 Административная панель

**Разделы:**
1. **Пользователи**
   - Таблица с фильтрацией и поиском
   - Управление ролями
   - Блокировка/разблокировка
   - Экспорт данных

2. **Потоки обучения**
   - CRUD операции
   - Drag & Drop для изменения порядка этапов
   - Предпросмотр потока
   - Статистика использования

3. **Контент**
   - Библиотека статей с категориями
   - Редактор заданий
   - Конструктор квизов
   - Управление медиафайлами

4. **Аналитика**
   - Дашборд с ключевыми метриками
   - Графики прохождения
   - Отчеты по пользователям
   - Экспорт в CSV/Excel

#### 4.4.2 Редакторы контента

**Редактор статей:**
- Split-view: Markdown слева, превью справа
- Панель инструментов для вставки элементов
- Загрузка изображений drag & drop
- Автосохранение
- История изменений

**Конструктор квизов:**
- Добавление/удаление вопросов
- Drag & Drop для изменения порядка
- Валидация (минимум 1 правильный ответ)
- Предпросмотр квиза
- Импорт/экспорт вопросов

## 5. UI/UX требования

### 5.1 Дизайн-система

#### 5.1.1 Принципы дизайна

1. **Telegram-native** - использование стилей и паттернов Telegram
2. **Минимализм** - фокус на контенте, минимум декоративных элементов
3. **Доступность** - WCAG 2.1 AA compliance
4. **Адаптивность** - работа на всех размерах экранов
5. **Темная тема** - обязательная поддержка

#### 5.1.2 Цветовая палитра

```scss
// Основные цвета (адаптируются под тему Telegram)
$primary: var(--tg-theme-button-color);
$text: var(--tg-theme-text-color);
$background: var(--tg-theme-bg-color);
$secondary-bg: var(--tg-theme-secondary-bg-color);

// Семантические цвета
$success: #34C759;
$warning: #FF9500;
$error: #FF3B30;
$info: #007AFF;

// Градиенты для прогресса
$progress-gradient: linear-gradient(90deg, #007AFF, #34C759);
```

#### 5.1.3 Типографика

```scss
// Использование системных шрифтов
$font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

// Размеры
$text-xs: 12px;
$text-sm: 14px;
$text-base: 16px;
$text-lg: 18px;
$text-xl: 20px;
$text-2xl: 24px;
```

### 5.2 Компоненты UI

#### 5.2.1 Атомарные компоненты

```typescript
// Примеры базовых компонентов
<Button variant="primary|secondary|ghost" size="sm|md|lg" />
<Input type="text|password|number" error={boolean} />
<Card elevated={boolean} interactive={boolean} />
<Progress value={number} max={number} showLabel={boolean} />
<Avatar src={string} size="sm|md|lg" fallback={string} />
<Badge variant="success|warning|error|info" />
```

#### 5.2.2 Анимации и переходы

```typescript
// Базовые анимации
const animations = {
  // Появление элементов
  fadeIn: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.3 }
  },
  
  // Успешное действие
  success: {
    scale: [1, 1.2, 1],
    transition: { duration: 0.4 }
  },
  
  // Загрузка
  skeleton: {
    background: linearGradient(['#f0f0f0', '#e0e0e0', '#f0f0f0']),
    animation: 'shimmer 1.5s infinite'
  }
};
```

### 5.3 Адаптивный дизайн

```scss
// Breakpoints
$mobile: 320px;
$tablet: 768px;
$desktop: 1024px;

// Пример адаптивной сетки
.flow-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
  
  @media (min-width: $tablet) {
    grid-template-columns: repeat(2, 1fr);
  }
  
  @media (min-width: $desktop) {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

## 6. Механики работы приложения

### 6.1 Навигация и маршрутизация

#### 6.1.1 Структура маршрутов

```typescript
const routes = {
  // Публичные маршруты
  '/auth': AuthPage,
  '/auth/telegram-callback': TelegramCallback,
  
  // Защищенные маршруты (все роли)
  '/': Dashboard,
  '/profile': Profile,
  '/flows/:flowId': FlowDetail,
  '/flows/:flowId/steps/:stepId': StepContent,
  
  // Buddy маршруты
  '/buddy': BuddyDashboard,
  '/buddy/flows': FlowSelector,
  '/buddy/flows/:flowId/assign': AssignFlow,
  '/buddy/mentees/:userId': MenteeProgress,
  
  // Moderator маршруты
  '/admin': AdminDashboard,
  '/admin/users': UsersManagement,
  '/admin/flows': FlowsManagement,
  '/admin/flows/:flowId/edit': FlowEditor,
  '/admin/content': ContentLibrary,
  '/admin/analytics': Analytics,
};
```

#### 6.1.2 Защита маршрутов

```typescript
// HOC для защиты маршрутов
const ProtectedRoute = ({ 
  component: Component, 
  requiredRoles = [] 
}) => {
  const { user, isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/auth" />;
  }
  
  if (requiredRoles.length && !hasAnyRole(user, requiredRoles)) {
    return <Navigate to="/" />;
  }
  
  return <Component />;
};
```

### 6.2 Управление состоянием

#### 6.2.1 Auth Slice

```typescript
interface AuthState {
  user: User | null;
  tokens: {
    access: string;
    refresh: string;
  } | null;
  isLoading: boolean;
  error: string | null;
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    loginStart: (state) => {
      state.isLoading = true;
      state.error = null;
    },
    loginSuccess: (state, action) => {
      state.user = action.payload.user;
      state.tokens = action.payload.tokens;
      state.isLoading = false;
    },
    loginFailure: (state, action) => {
      state.error = action.payload;
      state.isLoading = false;
    },
    logout: (state) => {
      state.user = null;
      state.tokens = null;
    }
  }
});
```

#### 6.2.2 RTK Query API

```typescript
const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api',
    prepareHeaders: (headers, { getState }) => {
      const token = selectAccessToken(getState());
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['User', 'Flow', 'Progress'],
  endpoints: (builder) => ({
    // Flows
    getMyFlows: builder.query<Flow[], void>({
      query: () => '/my/flows',
      providesTags: ['Flow'],
    }),
    
    // Progress
    getFlowProgress: builder.query<Progress, string>({
      query: (flowId) => `/my/progress/${flowId}`,
      providesTags: (result, error, flowId) => [
        { type: 'Progress', id: flowId }
      ],
    }),
    
    // Mutations
    completeStep: builder.mutation<void, CompleteStepParams>({
      query: ({ flowId, stepId, data }) => ({
        url: `/flows/${flowId}/steps/${stepId}/complete`,
        method: 'POST',
        body: data,
      }),
      invalidatesTags: (result, error, { flowId }) => [
        { type: 'Progress', id: flowId }
      ],
    }),
  }),
});
```

### 6.3 Обработка ошибок

#### 6.3.1 Глобальный обработчик

```typescript
// Error Boundary Component
class ErrorBoundary extends Component {
  state = { hasError: false, error: null };
  
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  
  componentDidCatch(error, errorInfo) {
    // Отправка в систему логирования
    console.error('Error caught by boundary:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />;
    }
    
    return this.props.children;
  }
}
```

#### 6.3.2 Toast уведомления

```typescript
// Toast система
const toastSlice = createSlice({
  name: 'toast',
  initialState: { toasts: [] },
  reducers: {
    showToast: (state, action) => {
      state.toasts.push({
        id: Date.now(),
        ...action.payload,
      });
    },
    hideToast: (state, action) => {
      state.toasts = state.toasts.filter(
        toast => toast.id !== action.payload
      );
    },
  },
});

// Hook для использования
const useToast = () => {
  const dispatch = useDispatch();
  
  return {
    success: (message) => dispatch(showToast({ 
      type: 'success', 
      message 
    })),
    error: (message) => dispatch(showToast({ 
      type: 'error', 
      message 
    })),
    info: (message) => dispatch(showToast({ 
      type: 'info', 
      message 
    })),
  };
};
```

### 6.4 Оптимизация производительности

#### 6.4.1 Code Splitting

```typescript
// Ленивая загрузка страниц
const AdminDashboard = lazy(() => 
  import('./pages/admin/Dashboard')
);

const FlowEditor = lazy(() => 
  import('./pages/admin/FlowEditor')
);

// Использование с Suspense
<Suspense fallback={<PageLoader />}>
  <Routes>
    <Route path="/admin" element={<AdminDashboard />} />
    <Route path="/admin/flows/:id/edit" element={<FlowEditor />} />
  </Routes>
</Suspense>
```

#### 6.4.2 Мемоизация

```typescript
// Мемоизация тяжелых вычислений
const useFlowProgress = (flowId: string) => {
  const steps = useSelector(state => 
    selectFlowSteps(state, flowId)
  );
  
  const progress = useMemo(() => {
    const completed = steps.filter(s => s.status === 'completed');
    return (completed.length / steps.length) * 100;
  }, [steps]);
  
  return progress;
};

// Мемоизация компонентов
const FlowCard = memo(({ flow, onSelect }) => {
  // Компонент перерендерится только при изменении flow или onSelect
  return (
    <Card onClick={() => onSelect(flow.id)}>
      <h3>{flow.title}</h3>
      <Progress value={flow.progress} />
    </Card>
  );
});
```

## 7. Структура проекта

### 7.1 Файловая структура

```
frontend/
├── public/
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── app/                    # Корневые компоненты и провайдеры
│   │   ├── App.tsx
│   │   ├── providers/          # Redux, Router, Theme провайдеры
│   │   └── store.ts           
│   ├── features/               # Feature-sliced модули
│   │   ├── auth/
│   │   │   ├── api/           # RTK Query endpoints
│   │   │   ├── components/    # Компоненты авторизации
│   │   │   ├── hooks/         # Кастомные хуки
│   │   │   ├── slice.ts       # Redux slice
│   │   │   └── types.ts       # TypeScript типы
│   │   ├── flows/
│   │   ├── progress/
│   │   └── users/
│   ├── pages/                  # Страницы приложения
│   │   ├── common/            # Общие страницы
│   │   ├── user/              # Страницы пользователя
│   │   ├── buddy/             # Страницы бадди
│   │   └── admin/             # Административные страницы
│   ├── shared/                 # Переиспользуемый код
│   │   ├── api/               # Базовая конфигурация API
│   │   ├── components/        # UI компоненты
│   │   ├── hooks/             # Общие хуки
│   │   ├── utils/             # Утилиты
│   │   └── types/             # Общие типы
│   ├── styles/                 # Глобальные стили
│   └── main.tsx               # Точка входа
├── .env.example               # Пример переменных окружения
├── .eslintrc.json            # ESLint конфигурация
├── .prettierrc               # Prettier конфигурация
├── Dockerfile                # Docker образ
├── docker-compose.yml        # Docker Compose конфигурация
├── package.json
├── tsconfig.json            # TypeScript конфигурация
├── vite.config.ts          # Vite конфигурация
└── README.md
```

### 7.2 Примеры компонентов

#### 7.2.1 Feature Component

```typescript
// features/flows/components/FlowProgress.tsx
import { FC } from 'react';
import { useFlowProgress } from '../hooks/useFlowProgress';
import { Progress, Card } from '@/shared/components';

interface FlowProgressProps {
  flowId: string;
  showDetails?: boolean;
}

export const FlowProgress: FC<FlowProgressProps> = ({ 
  flowId, 
  showDetails = false 
}) => {
  const { progress, currentStep, isLoading } = useFlowProgress(flowId);
  
  if (isLoading) {
    return <Progress.Skeleton />;
  }
  
  return (
    <Card>
      <div className="space-y-4">
        <Progress 
          value={progress} 
          max={100}
          className="h-2"
        />
        
        {showDetails && currentStep && (
          <div className="text-sm text-gray-600">
            Текущий этап: {currentStep.title}
          </div>
        )}
      </div>
    </Card>
  );
};
```

#### 7.2.2 Page Component

```typescript
// pages/user/FlowDetail.tsx
import { FC } from 'react';
import { useParams } from 'react-router-dom';
import { useGetFlowQuery } from '@/features/flows/api';
import { FlowHeader, FlowSteps } from '@/features/flows/components';
import { PageLayout } from '@/shared/components';

export const FlowDetailPage: FC = () => {
  const { flowId } = useParams<{ flowId: string }>();
  const { data: flow, isLoading } = useGetFlowQuery(flowId!);
  
  if (isLoading) {
    return <PageLayout.Loading />;
  }
  
  if (!flow) {
    return <PageLayout.NotFound />;
  }
  
  return (
    <PageLayout
      title={flow.title}
      backButton
    >
      <div className="space-y-6">
        <FlowHeader flow={flow} />
        <FlowSteps flowId={flow.id} />
      </div>
    </PageLayout>
  );
};
```

## 8. API интеграция

### 8.1 Конфигурация клиента

```typescript
// shared/api/client.ts
import axios from 'axios';
import { store } from '@/app/store';
import { refreshTokens } from '@/features/auth/slice';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

// Axios instance
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    const state = store.getState();
    const token = state.auth.tokens?.access;
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor для обновления токенов
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        await store.dispatch(refreshTokens());
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Редирект на авторизацию
        window.location.href = '/auth';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);
```

### 8.2 Типизация API

```typescript
// shared/api/types.ts
export interface ApiResponse<T> {
  data: T;
  meta?: {
    pagination?: {
      page: number;
      pageSize: number;
      total: number;
    };
  };
}

export interface ApiError {
  message: string;
  errors?: Record<string, string[]>;
  statusCode: number;
}

// Type guards
export const isApiError = (error: unknown): error is ApiError => {
  return (
    typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    'statusCode' in error
  );
};
```

### 8.3 API хуки

```typescript
// features/flows/api/hooks.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { flowsApi } from './client';

// Получение потоков
export const useFlows = () => {
  return useQuery({
    queryKey: ['flows'],
    queryFn: flowsApi.getMyFlows,
    staleTime: 5 * 60 * 1000, // 5 минут
  });
};

// Завершение этапа
export const useCompleteStep = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: flowsApi.completeStep,
    onSuccess: (_, variables) => {
      // Инвалидация кеша
      queryClient.invalidateQueries(['flows']);
      queryClient.invalidateQueries(['progress', variables.flowId]);
    },
  });
};
```

## 9. Безопасность

### 9.1 Аутентификация

#### 9.1.1 Telegram Mini App Auth

```typescript
// features/auth/services/telegram.ts
import { validateTelegramWebAppData } from '@/shared/utils/telegram';

export const authenticateWithTelegram = async () => {
  // Получение InitData из Telegram
  const tg = window.Telegram?.WebApp;
  
  if (!tg?.initDataUnsafe) {
    throw new Error('Telegram WebApp не инициализирован');
  }
  
  // Валидация данных
  const isValid = validateTelegramWebAppData(
    tg.initData,
    process.env.TELEGRAM_BOT_TOKEN
  );
  
  if (!isValid) {
    throw new Error('Невалидные данные Telegram');
  }
  
  // Отправка на бекенд
  const response = await apiClient.post('/auth/telegram', {
    initData: tg.initData,
  });
  
  return response.data;
};
```

#### 9.1.2 Локальная авторизация (dev mode)

```typescript
// features/auth/components/LocalAuth.tsx
export const LocalAuth: FC = () => {
  const [login] = useLoginMutation();
  
  const onSubmit = async (data: LoginForm) => {
    try {
      await login({
        email: data.email,
        password: data.password,
      }).unwrap();
      
      navigate('/');
    } catch (error) {
      toast.error('Неверный email или пароль');
    }
  };
  
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* Форма логина */}
    </form>
  );
};
```

### 9.2 Защита данных

#### 9.2.1 Санитизация контента

```typescript
// shared/utils/sanitize.ts
import DOMPurify from 'dompurify';

export const sanitizeMarkdown = (markdown: string): string => {
  // Конвертация Markdown в HTML
  const html = markdownToHtml(markdown);
  
  // Санитизация HTML
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: [
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'p', 'br', 'strong', 'em', 'u', 's',
      'ul', 'ol', 'li', 'blockquote', 'code', 'pre',
      'a', 'img', 'table', 'thead', 'tbody', 'tr', 'th', 'td'
    ],
    ALLOWED_ATTR: ['href', 'src', 'alt', 'title', 'class'],
  });
};
```

#### 9.2.2 Валидация форм

```typescript
// features/flows/schemas/quiz.ts
import { z } from 'zod';

export const quizAnswerSchema = z.object({
  questionId: z.string().uuid(),
  answerId: z.string().uuid(),
});

export const createQuizSchema = z.object({
  title: z.string().min(3).max(100),
  description: z.string().max(500).optional(),
  passingScore: z.number().min(0).max(100),
  questions: z.array(
    z.object({
      question: z.string().min(5).max(500),
      answers: z.array(
        z.object({
          text: z.string().min(1).max(200),
          isCorrect: z.boolean(),
          explanation: z.string().max(500).optional(),
        })
      ).length(5), // Ровно 5 ответов
    })
  ).min(1).max(15), // От 1 до 15 вопросов
});
```

## 10. Локальная разработка

### 10.1 Переменные окружения

```bash
# .env.development
VITE_API_URL=http://localhost:8000/api
VITE_TELEGRAM_BOT_TOKEN=test-token
VITE_ENABLE_DEV_MODE=true
VITE_MOCK_TELEGRAM_DATA=true
```

### 10.2 Mock Telegram WebApp

```typescript
// shared/mocks/telegram.ts
export const mockTelegramWebApp = () => {
  if (!window.Telegram) {
    window.Telegram = {
      WebApp: {
        initData: JSON.stringify({
          user: {
            id: 123456789,
            first_name: 'Test',
            last_name: 'User',
            username: 'testuser',
          },
          auth_date: Math.floor(Date.now() / 1000),
          hash: 'mock-hash',
        }),
        initDataUnsafe: {
          user: {
            id: 123456789,
            first_name: 'Test',
            last_name: 'User',
            username: 'testuser',
          },
        },
        ready: () => {},
        expand: () => {},
        close: () => {},
        MainButton: {
          show: () => {},
          hide: () => {},
          setText: () => {},
          onClick: () => {},
        },
        BackButton: {
          show: () => {},
          hide: () => {},
          onClick: () => {},
        },
        themeParams: {
          bg_color: '#ffffff',
          text_color: '#000000',
          hint_color: '#707579',
          link_color: '#3390ec',
          button_color: '#3390ec',
          button_text_color: '#ffffff',
        },
      },
    };
  }
};
```

### 10.3 Скрипты разработки

```json
// package.json
{
  "scripts": {
    "dev": "vite",
    "dev:mock": "VITE_MOCK_API=true vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest run --coverage",
    "lint": "eslint src --ext ts,tsx",
    "lint:fix": "eslint src --ext ts,tsx --fix",
    "format": "prettier --write \"src/**/*.{ts,tsx,css}\"",
    "typecheck": "tsc --noEmit",
    "storybook": "storybook dev -p 6006",
    "build-storybook": "storybook build"
  }
}
```

## 11. Docker конфигурация

### 11.1 Dockerfile

```dockerfile
# Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

# Копирование package files
COPY package*.json ./
RUN npm ci --only=production

# Копирование исходного кода
COPY . .

# Сборка приложения
RUN npm run build

# Production image
FROM nginx:alpine

# Копирование конфигурации nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Копирование собранного приложения
COPY --from=builder /app/dist /usr/share/nginx/html

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q --spider http://localhost || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 11.2 Docker Compose интеграция

```yaml
# docker-compose.yml (дополнение к существующему)
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    environment:
      - VITE_API_URL=http://backend:8000/api
    depends_on:
      - backend
    networks:
      - budtest-network

  # Для разработки
  frontend-dev:
    image: node:20-alpine
    working_dir: /app
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000/api
    command: npm run dev -- --host 0.0.0.0
    networks:
      - budtest-network
```

### 11.3 Nginx конфигурация

```nginx
# nginx.conf
server {
    listen 80;
    server_name localhost;
    
    root /usr/share/nginx/html;
    index index.html;
    
    # Gzip сжатие
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/javascript application/xml+rss 
               application/json;
    
    # Кеширование статики
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Проксирование API запросов (для dev)
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 12. Критерии приемки

### 12.1 Функциональные требования

- [ ] Авторизация через Telegram Mini App работает корректно
- [ ] Локальная авторизация доступна в dev режиме
- [ ] Все роли имеют доступ только к своему функционалу
- [ ] Прогрессивное раскрытие контента работает правильно
- [ ] Все типы контента (статьи, задания, квизы) отображаются корректно
- [ ] Система уведомлений работает
- [ ] Административная панель полностью функциональна

### 12.2 Технические требования

- [ ] Приложение работает в Telegram на iOS и Android
- [ ] Поддержка светлой и темной темы
- [ ] Время загрузки главной страницы < 2 секунды
- [ ] Размер бандла < 500KB (gzipped)
- [ ] Покрытие тестами > 80%
- [ ] Отсутствие критических уязвимостей (npm audit)
- [ ] Соответствие WCAG 2.1 AA

### 12.3 UX требования

- [ ] Все интерактивные элементы имеют визуальную обратную связь
- [ ] Состояния загрузки отображаются для всех асинхронных операций
- [ ] Ошибки обрабатываются gracefully с понятными сообщениями
- [ ] Навигация интуитивна и последовательна
- [ ] Приложение работает офлайн (базовый функционал)

### 12.4 Документация

- [ ] README с инструкциями по запуску
- [ ] Документация API в Storybook
- [ ] Комментарии к сложному коду
- [ ] Changelog с историей изменений

---

## Заключение

Данное техническое задание описывает комплексную систему онбординга с современным, удобным интерфейсом, интегрированным в экосистему Telegram. Следование описанным принципам и практикам позволит создать качественный продукт, который решит поставленные бизнес-задачи и обеспечит отличный пользовательский опыт.

При разработке важно:
1. Регулярно тестировать в реальном Telegram окружении
2. Оптимизировать производительность для мобильных устройств
3. Следить за обновлениями Telegram Mini Apps API
4. Поддерживать тесную связь с бекенд-командой

Успехов в разработке! 🚀