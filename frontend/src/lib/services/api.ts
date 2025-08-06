/**
 * API client for communicating with the Bright Ideas backend - New Architecture
 */
import type {
  Idea,
  IdeaDetail,
  IdeaCreate,
  IdeaUpdate,
  IdeaStats,
  IdeaSummary,
  RefinementSession,
  RefinementSessionCreate,
  RefinementAnswersSubmit,
  Plan,
  PlanCreate,
  PlanUpdate,
  ApiError
} from '$lib/types';

// Configuration - with fallback for build environments
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://bright-ideas-backend.onrender.com';
const API_PREFIX = '/api/v1';

// Debug logging for API configuration (dev only)
if (import.meta.env.MODE === 'development') {
  console.log('API Configuration (New Architecture):', {
    API_BASE_URL,
    API_PREFIX,
    VITE_API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
    env_mode: import.meta.env.MODE,
    env_prod: import.meta.env.PROD
  });
}

// Additional validation
if (API_BASE_URL.includes('your-backend-url')) {
  console.error('❌ CRITICAL: API_BASE_URL is using placeholder value!', API_BASE_URL);
  throw new Error('API configuration error: Invalid backend URL');
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${API_PREFIX}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      if (import.meta.env.MODE === 'development') {
        console.log(`API Request: ${config.method || 'GET'} ${url}`);
      }
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const error: ApiError = await response.json().catch(() => ({
          detail: `HTTP ${response.status}: ${response.statusText}`
        }));
        console.error(`API Error: ${config.method || 'GET'} ${url}`, {
          status: response.status,
          statusText: response.statusText,
          error: error.detail
        });
        throw new Error(error.detail);
      }

      // Handle empty responses (like DELETE)
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      } else {
        return response as unknown as T;
      }
    } catch (error) {
      if (error instanceof Error) {
        console.error(`Network Error: ${config.method || 'GET'} ${url}`, error);
        throw error;
      }
      console.error(`Unknown Error: ${config.method || 'GET'} ${url}`, error);
      throw new Error('Network error occurred');
    }
  }

  // Helper method for file downloads
  private async downloadFile(
    endpoint: string,
    filename: string
  ): Promise<Blob> {
    const url = `${this.baseUrl}${API_PREFIX}${endpoint}`;
    
    try {
      if (import.meta.env.MODE === 'development') {
        console.log(`Download Request: GET ${url}`);
      }
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Download failed: ${response.status} ${response.statusText}`);
      }
      
      return response.blob();
    } catch (error) {
      console.error(`Download Error: GET ${url}`, error);
      throw error;
    }
  }

  // ====================================
  // IDEA API METHODS
  // ====================================

  async createIdea(idea: IdeaCreate): Promise<Idea> {
    return this.request<Idea>('/ideas/', {
      method: 'POST',
      body: JSON.stringify(idea),
    });
  }

  async getIdeas(params?: {
    skip?: number;
    limit?: number;
    search?: string;
    tags?: string[];
    status?: string;
  }): Promise<Idea[]> {
    const searchParams = new URLSearchParams();
    
    if (params?.skip) searchParams.set('skip', params.skip.toString());
    if (params?.limit) searchParams.set('limit', params.limit.toString());
    if (params?.search) searchParams.set('search', params.search);
    if (params?.status) searchParams.set('status', params.status);
    if (params?.tags) {
      params.tags.forEach(tag => searchParams.append('tags', tag));
    }

    const query = searchParams.toString();
    return this.request<Idea[]>(`/ideas/${query ? `?${query}` : ''}`);
  }

  async getIdea(ideaId: string): Promise<IdeaDetail> {
    return this.request<IdeaDetail>(`/ideas/${ideaId}`);
  }

  async updateIdea(ideaId: string, update: IdeaUpdate): Promise<Idea> {
    return this.request<Idea>(`/ideas/${ideaId}`, {
      method: 'PUT',
      body: JSON.stringify(update),
    });
  }

  async deleteIdea(ideaId: string): Promise<void> {
    await this.request(`/ideas/${ideaId}`, {
      method: 'DELETE',
    });
  }

  async getIdeaStats(): Promise<IdeaStats> {
    return this.request<IdeaStats>('/ideas/stats');
  }

  async getRecentIdeas(limit = 5): Promise<Idea[]> {
    return this.request<Idea[]>(`/ideas/recent?limit=${limit}`);
  }

  async getIdeaSummary(ideaId: string): Promise<IdeaSummary> {
    return this.request<IdeaSummary>(`/ideas/${ideaId}/summary`);
  }

  // ====================================
  // REFINEMENT API METHODS
  // ====================================

  async createRefinementSession(data: RefinementSessionCreate): Promise<RefinementSession> {
    return this.request<RefinementSession>('/refinement/sessions/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getRefinementSession(sessionId: string): Promise<RefinementSession> {
    return this.request<RefinementSession>(`/refinement/sessions/${sessionId}`);
  }

  async getIdeaRefinementSessions(ideaId: string): Promise<RefinementSession[]> {
    return this.request<RefinementSession[]>(`/refinement/ideas/${ideaId}/sessions/`);
  }

  async submitRefinementAnswers(
    sessionId: string, 
    data: RefinementAnswersSubmit
  ): Promise<RefinementSession> {
    return this.request<RefinementSession>(`/refinement/sessions/${sessionId}/answers/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async completeRefinementSession(sessionId: string): Promise<RefinementSession> {
    return this.request<RefinementSession>(`/refinement/sessions/${sessionId}/complete/`, {
      method: 'POST',
    });
  }

  // Test endpoint for question generation
  async generateTestQuestions(ideaId: string): Promise<{ questions: any[] }> {
    return this.request<{ questions: any[] }>(`/refinement/questions/generate/`, {
      method: 'POST',
      body: JSON.stringify({ idea_id: ideaId }),
    });
  }

  // ====================================
  // PLAN API METHODS
  // ====================================

  async generatePlan(refinementSessionId: string): Promise<Plan> {
    return this.request<Plan>('/plans/generate/', {
      method: 'POST',
      body: JSON.stringify({ refinement_session_id: refinementSessionId }),
    });
  }

  async getPlan(planId: string): Promise<Plan> {
    return this.request<Plan>(`/plans/${planId}`);
  }

  async getIdeaPlans(ideaId: string): Promise<Plan[]> {
    return this.request<Plan[]>(`/plans/ideas/${ideaId}`);
  }

  async updatePlan(planId: string, update: PlanUpdate): Promise<Plan> {
    return this.request<Plan>(`/plans/${planId}`, {
      method: 'PUT',
      body: JSON.stringify(update),
    });
  }

  async activatePlan(planId: string): Promise<Plan> {
    return this.request<Plan>(`/plans/${planId}/activate`, {
      method: 'POST',
    });
  }

  async deletePlan(planId: string): Promise<void> {
    await this.request(`/plans/${planId}`, {
      method: 'DELETE',
    });
  }

  async uploadPlan(upload: { idea_id: string; content: string; title?: string }): Promise<Plan> {
    return this.request<Plan>('/plans/upload/', {
      method: 'POST',
      body: JSON.stringify(upload),
    });
  }

  // Export methods
  async exportPlanAsJson(planId: string): Promise<Blob> {
    return this.downloadFile(`/plans/${planId}/export/json`, `plan_${planId}.json`);
  }

  async exportPlanAsMarkdown(planId: string): Promise<Blob> {
    return this.downloadFile(`/plans/${planId}/export/markdown`, `plan_${planId}.md`);
  }

  // Test endpoint for plan generation
  async testPlanGeneration(
    ideaId: string, 
    answers: Record<string, string>
  ): Promise<{ summary: string; steps: any[]; resources: any[] }> {
    return this.request<{ summary: string; steps: any[]; resources: any[] }>('/plans/test-generation/', {
      method: 'POST',
      body: JSON.stringify({ idea_id: ideaId, answers }),
    });
  }

  // ====================================
  // UTILITY METHODS
  // ====================================

  // Health check
  async healthCheck(): Promise<{ 
    status: string; 
    version: string; 
    architecture: string;
    features: string[];
  }> {
    return this.request<{ 
      status: string; 
      version: string; 
      architecture: string;
      features: string[];
    }>('/health');
  }

  // Helper method to trigger file download in browser
  downloadBlob(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }

  // Helper method for exporting and downloading plans
  async downloadPlanJson(planId: string, filename?: string): Promise<void> {
    const blob = await this.exportPlanAsJson(planId);
    this.downloadBlob(blob, filename || `plan_${planId}.json`);
  }

  async downloadPlanMarkdown(planId: string, filename?: string): Promise<void> {
    const blob = await this.exportPlanAsMarkdown(planId);
    this.downloadBlob(blob, filename || `plan_${planId}.md`);
  }
}

// Export singleton instance
export const api = new ApiClient();
export default api;