/**
 * TypeScript type definitions for Bright Ideas frontend
 */

export interface Idea {
  id: string;
  title: string;
  original_description: string;
  refined_description?: string;
  problem_statement?: string;
  target_audience?: string;
  implementation_notes: Record<string, any>;
  tags: string[];
  status: 'captured' | 'refined' | 'building' | 'completed';
  created_at: string;
  updated_at: string;
}

export interface IdeaCreate {
  title: string;
  original_description: string;
  tags: string[];
}

export interface IdeaUpdate {
  title?: string;
  refined_description?: string;
  problem_statement?: string;
  target_audience?: string;
  implementation_notes?: Record<string, any>;
  tags?: string[];
  status?: 'captured' | 'refined' | 'building' | 'completed';
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: {
    questions?: string[];
    refined_data?: Record<string, any>;
  };
}

export interface Conversation {
  id: string;
  idea_id: string;
  mode: 'capture' | 'build';
  messages: ChatMessage[];
  context: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface ConversationCreate {
  idea_id: string;
  mode: 'capture' | 'build';
  initial_message?: string;
}

export interface MessageCreate {
  content: string;
  role: 'user' | 'assistant';
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  context?: Record<string, any>;
}

export interface ChatResponse {
  message: string;
  conversation_id: string;
  suggestions?: string[];
  context?: Record<string, any>;
}

export interface BuildPlan {
  id: string;
  idea_id: string;
  plan_data: {
    overview: string;
    components: PlanComponent[];
    phases: PlanPhase[];
    success_criteria: string[];
    full_content?: string;
  };
  export_configs: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface PlanComponent {
  name: string;
  description: string;
}

export interface PlanPhase {
  name: string;
  duration: string;
  tasks: string[];
  deliverables: string[];
}

export interface BuildPlanCreate {
  idea_id: string;
  plan_data: Record<string, any>;
}

export interface BuildPlanUpdate {
  plan_data?: Record<string, any>;
  export_configs?: Record<string, any>;
}

export interface Export {
  id: string;
  build_plan_id: string;
  export_type: string;
  file_data: Record<string, string>;
  created_at: string;
}

export interface ExportCreate {
  build_plan_id: string;
  export_type: string;
  file_data: Record<string, string>;
}

export interface ApiError {
  detail: string;
}

export interface IdeaStats {
  total_ideas: number;
  status_distribution: Record<string, number>;
  popular_tags: [string, number][];
}

// UI State Types
export interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
}

export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface Modal {
  id: string;
  isOpen: boolean;
  title?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

// Form Types
export interface IdeaCaptureForm {
  title: string;
  description: string;
  tags: string[];
}

export interface SearchFilters {
  search?: string;
  tags?: string[];
  status?: string;
  sortBy?: 'created_at' | 'updated_at' | 'title';
  sortOrder?: 'asc' | 'desc';
}

// Navigation Types
export interface NavItem {
  label: string;
  href: string;
  icon?: string;
  active?: boolean;
}

export interface BreadcrumbItem {
  label: string;
  href?: string;
}