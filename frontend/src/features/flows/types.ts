export interface Article {
  id: number;
  title: string;
  slug: string;
  summary: string;
  content?: string;
  article_type: 'guide' | 'article';
  reading_time_minutes: number;
  difficulty_level: 'beginner' | 'intermediate' | 'advanced';
  view_count: number;
  published_at: string | null;
}

export interface Task {
  id: number;
  title: string;
  description: string;
  instruction: string;
  hint: string | null;
}

export interface QuizAnswer {
  id: number;
  answer_text: string;
  order: number;
}

export interface QuizQuestion {
  id: number;
  question: string;
  order: number;
  answers: QuizAnswer[];
}

export interface Quiz {
  id: number;
  title: string;
  description: string | null;
  passing_score_percentage: number;
  shuffle_questions: boolean;
  shuffle_answers: boolean;
  total_questions: number;
  questions: QuizQuestion[];
  is_active: boolean;
}

export interface FlowStep {
  id: number;
  title: string;
  description: string;
  order: number;
  is_active: boolean;
  article: Article;
  task: Task;
  quiz: Quiz;
}

export interface Flow {
  id: number;
  title: string;
  description: string;
  is_mandatory: boolean;
  is_active: boolean;
  total_steps: number;
  steps: FlowStep[];
}

export interface BuddyUser {
  id: number;
  name: string;
  telegram_id: string;
  position: string | null;
  department: string | null;
  is_active: boolean;
  roles: string[];
  created_at: string;
}

export interface FlowBuddy {
  id: number;
  buddy_user: BuddyUser;
  can_pause_flow: boolean;
  can_resume_flow: boolean;
  can_extend_deadline: boolean;
  assigned_by_name: string;
  assigned_at: string;
  is_active: boolean;
  created_at: string;
}

export interface UserFlow {
  id: number;
  user: BuddyUser;
  flow: Flow;
  status: 'not_started' | 'in_progress' | 'completed' | 'paused' | 'suspended';
  current_step: FlowStep | null;
  progress_percentage: number;
  is_overdue: boolean;
  flow_buddies: FlowBuddy[];
  paused_at: string | null;
  pause_reason: string | null;
  expected_completion_date: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface User {
  id: number;
  name: string;
  telegram_username?: string;
} 