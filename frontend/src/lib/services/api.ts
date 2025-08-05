/**
 * API client for communicating with the Bright Ideas backend
 */
import type {
  Idea,
  IdeaCreate,
  IdeaUpdate,
  IdeaStats,
  Conversation,
  ConversationCreate,
  MessageCreate,
  ChatRequest,
  ChatResponse,
  BuildPlan,
  BuildPlanCreate,
  BuildPlanUpdate,
  Export,
  ExportCreate,
  ApiError
} from '$lib/types';

// Configuration - with fallback for build environments
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://bright-ideas-backend.onrender.com';
const API_PREFIX = '/api/v1';

// Debug logging for API configuration
console.log('API Configuration (v2):', {
  API_BASE_URL,
  API_PREFIX,
  VITE_API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
  env_mode: import.meta.env.MODE,
  env_prod: import.meta.env.PROD
});

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
      console.log(`API Request: ${config.method || 'GET'} ${url}`);
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

      // Handle empty responses
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

  // Idea API methods
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

  async getIdea(ideaId: string): Promise<Idea> {
    return this.request<Idea>(`/ideas/${ideaId}`);
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
    return this.request<IdeaStats>('/ideas/stats/');
  }

  async getRecentIdeas(limit = 5): Promise<Idea[]> {
    return this.request<Idea[]>(`/ideas/recent/?limit=${limit}`);
  }

  // Conversation API methods
  async createConversation(conversation: ConversationCreate): Promise<Conversation> {
    return this.request<Conversation>('/conversations/', {
      method: 'POST',
      body: JSON.stringify(conversation),
    });
  }

  async startRefinementConversation(ideaId: string): Promise<Conversation> {
    return this.request<Conversation>(`/conversations/refine/${ideaId}`, {
      method: 'POST',
    });
  }

  async getConversation(conversationId: string): Promise<Conversation> {
    return this.request<Conversation>(`/conversations/${conversationId}`);
  }

  async getIdeaConversations(ideaId: string, mode?: string): Promise<Conversation[]> {
    const query = mode ? `?mode=${mode}` : '';
    return this.request<Conversation[]>(`/conversations/idea/${ideaId}${query}`);
  }

  async addMessage(conversationId: string, message: MessageCreate): Promise<Conversation> {
    return this.request<Conversation>(`/conversations/${conversationId}/messages`, {
      method: 'POST',
      body: JSON.stringify(message),
    });
  }

  async chat(chatRequest: ChatRequest): Promise<ChatResponse> {
    return this.request<ChatResponse>('/conversations/chat', {
      method: 'POST',
      body: JSON.stringify(chatRequest),
    });
  }

  async updateConversationContext(
    conversationId: string, 
    context: Record<string, any>
  ): Promise<void> {
    await this.request(`/conversations/${conversationId}/context`, {
      method: 'PUT',
      body: JSON.stringify(context),
    });
  }

  async deleteConversation(conversationId: string): Promise<void> {
    await this.request(`/conversations/${conversationId}`, {
      method: 'DELETE',
    });
  }

  // Build Planning API methods
  async createBuildPlan(plan: BuildPlanCreate): Promise<BuildPlan> {
    return this.request<BuildPlan>('/planning/', {
      method: 'POST',
      body: JSON.stringify(plan),
    });
  }

  async getBuildPlan(planId: string): Promise<BuildPlan> {
    return this.request<BuildPlan>(`/planning/${planId}`);
  }

  async getIdeaBuildPlans(ideaId: string): Promise<BuildPlan[]> {
    return this.request<BuildPlan[]>(`/planning/idea/${ideaId}`);
  }

  async updateBuildPlan(planId: string, update: BuildPlanUpdate): Promise<BuildPlan> {
    return this.request<BuildPlan>(`/planning/${planId}`, {
      method: 'PUT',
      body: JSON.stringify(update),
    });
  }

  async addPlanComponent(
    planId: string, 
    component: { name: string; description: string }
  ): Promise<BuildPlan> {
    return this.request<BuildPlan>(`/planning/${planId}/components`, {
      method: 'POST',
      body: JSON.stringify(component),
    });
  }

  async updatePlanPhase(
    planId: string, 
    phaseIndex: number, 
    phaseData: Record<string, any>
  ): Promise<BuildPlan> {
    return this.request<BuildPlan>(`/planning/${planId}/phases/${phaseIndex}`, {
      method: 'PUT',
      body: JSON.stringify(phaseData),
    });
  }

  // Export API methods
  async createExport(exportData: ExportCreate): Promise<Export> {
    return this.request<Export>('/planning/exports/', {
      method: 'POST',
      body: JSON.stringify(exportData),
    });
  }

  async exportMarkdown(planId: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}${API_PREFIX}/planning/${planId}/export/markdown`);
    if (!response.ok) {
      throw new Error('Export failed');
    }
    return response.blob();
  }

  async exportJson(planId: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}${API_PREFIX}/planning/${planId}/export/json`);
    if (!response.ok) {
      throw new Error('Export failed');
    }
    return response.blob();
  }

  async previewMarkdownExport(planId: string): Promise<Record<string, any>> {
    return this.request<Record<string, any>>(`/planning/${planId}/preview/markdown`);
  }

  // Health check
  async healthCheck(): Promise<{ status: string; version: string }> {
    return this.request<{ status: string; version: string }>('/health');
  }
}

// Export singleton instance
export const api = new ApiClient();
export default api;