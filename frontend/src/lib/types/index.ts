/**
 * TypeScript type definitions for Bright Ideas frontend - New Architecture
 */

// ====================================
// CORE DATA TYPES (matching backend)
// ====================================

// Todo Types
export interface Todo {
  id: string;
  text: string;
  is_completed: boolean;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface TodoCreate {
  text: string;
}

export interface TodoUpdate {
  text?: string;
  is_completed?: boolean;
}

export interface Idea {
  id: string;
  title: string;
  original_description: string;
  tags: string[];
  status: "captured" | "refining" | "planned" | "archived";
  is_unrefined?: boolean; // Optional for backward compatibility
  created_at: string;
  updated_at: string;

  // Computed fields from backend
  refinement_sessions_count: number;
  plans_count: number;
  has_active_plan: boolean;
}

export interface IdeaDetail extends Idea {
  latest_session?: RefinementSession;
  active_plan?: Plan;
}

export interface IdeaCreate {
  title: string;
  original_description: string;
  tags: string[];
  is_unrefined?: boolean;
}

export interface IdeaUpdate {
  title?: string;
  original_description?: string;
  tags?: string[];
  status?: "captured" | "refining" | "planned" | "archived";
  is_unrefined?: boolean;
}

// ====================================
// REFINEMENT TYPES
// ====================================

export interface RefinementQuestion {
  id: string;
  question: string;
}

export interface RefinementSession {
  id: string;
  idea_id: string;
  questions: RefinementQuestion[];
  answers: Record<string, string>; // question_id -> answer
  is_complete: boolean;
  created_at: string;
  completed_at?: string;
}

export interface RefinementSessionCreate {
  idea_id: string;
}

export interface RefinementAnswersSubmit {
  answers: Record<string, string>;
}

// ====================================
// PLAN TYPES
// ====================================

export interface PlanStep {
  order: number;
  title: string;
  description: string;
  estimated_time?: string;
}

export interface PlanResource {
  title: string;
  url?: string;
  type: string; // 'tool', 'article', 'service', etc.
  description?: string;
}

export interface Plan {
  id: string;
  idea_id: string;
  refinement_session_id?: string;
  summary: string;
  steps: PlanStep[];
  resources: PlanResource[];
  status: "draft" | "generated" | "edited" | "published";
  is_active: boolean;
  content_markdown?: string;
  created_at: string;
  updated_at: string;
}

export interface PlanCreate {
  refinement_session_id: string;
  summary: string;
  steps: PlanStep[];
  resources: PlanResource[];
}

export interface PlanUpdate {
  summary?: string;
  steps?: PlanStep[];
  resources?: PlanResource[];
  status?: "draft" | "generated" | "edited" | "published";
}

// ====================================
// API RESPONSE TYPES
// ====================================

export interface ApiError {
  detail: string;
}

export interface IdeaStats {
  total_ideas: number;
  status_counts: Record<string, number>;
  ideas_with_plans: number;
  total_refinement_sessions: number;
  completed_refinement_sessions: number;
  average_sessions_per_idea: number;
}

export interface IdeaSummary {
  idea: {
    id: string;
    title: string;
    description: string;
    status: string;
    tags: string[];
    created_at: string;
    updated_at: string;
  };
  refinement_progress: {
    total_sessions: number;
    completed_sessions: number;
    latest_session?: RefinementSession;
  };
  planning_progress: {
    total_plans: number;
    has_active_plan: boolean;
    active_plan_id?: string;
  };
  next_steps: string[];
}

// ====================================
// UI STATE TYPES
// ====================================

export interface Toast {
  id: string;
  type: "success" | "error" | "warning" | "info";
  message: string;
  duration?: number;
  actionLabel?: string;
  actionCallback?: () => void;
}

export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface Modal {
  id: string;
  isOpen: boolean;
  title?: string;
  size?: "sm" | "md" | "lg" | "xl";
}

// ====================================
// FORM TYPES
// ====================================

export interface IdeaCaptureForm {
  title: string;
  description: string;
  tags: string[];
}

export interface RefinementForm {
  answers: Record<string, string>;
}

export interface SearchFilters {
  search?: string;
  tags?: string[];
  status?: string;
  sortBy?: "created_at" | "updated_at" | "title";
  sortOrder?: "asc" | "desc";
  includeArchived?: boolean;
}

// ====================================
// NAVIGATION TYPES
// ====================================

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

// ====================================
// COMPONENT PROPS TYPES
// ====================================

export interface RefinementFormProps {
  questions: RefinementQuestion[];
  answers: Record<string, string>;
  loading?: boolean;
  onSubmit: (answers: Record<string, string>) => void;
}

export interface PlanViewerProps {
  plan: Plan;
  showExportButtons?: boolean;
  onExport?: (format: "json" | "markdown") => void;
}

export interface ProgressIndicatorProps {
  current: number;
  total: number;
  label?: string;
}

// ====================================
// DEPRECATED TYPES (for cleanup reference)
// ====================================

// These types are no longer used with the new architecture:
// - ChatMessage (replaced with structured Q&A)
// - Conversation (replaced with RefinementSession)
// - ConversationCreate (replaced with RefinementSessionCreate)
// - MessageCreate (no longer needed)
// - ChatRequest/ChatResponse (replaced with structured submission)
// - BuildPlan (replaced with Plan)
// - BuildPlanCreate/Update (replaced with PlanCreate/Update)
// - Export/ExportCreate (simplified to direct download)
