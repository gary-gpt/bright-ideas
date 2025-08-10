/**
 * Svelte stores for idea management - New Architecture
 */
import { writable, derived, get } from "svelte/store";
import type {
  Idea,
  IdeaDetail,
  IdeaStats,
  IdeaSummary,
  SearchFilters,
  RefinementSession,
  Plan,
} from "$lib/types";
import { api } from "$lib/services/api";

// ====================================
// CORE STORES
// ====================================

// Ideas store
export const ideas = writable<Idea[]>([]);
export const currentIdea = writable<IdeaDetail | null>(null);
export const ideaStats = writable<IdeaStats | null>(null);

// Refinement stores
export const currentRefinementSession = writable<RefinementSession | null>(
  null,
);
export const refinementSessions = writable<RefinementSession[]>([]);

// Plan stores
export const currentPlan = writable<Plan | null>(null);
export const ideaPlans = writable<Plan[]>([]);

// Search and filter store
export const searchFilters = writable<SearchFilters>({
  search: "",
  tags: [],
  status: "",
  sortBy: "updated_at",
  sortOrder: "desc",
});

// Loading states
export const ideasLoading = writable(false);
export const ideaLoading = writable(false);
export const refinementLoading = writable(false);
export const planLoading = writable(false);

// ====================================
// DERIVED STORES
// ====================================

export const filteredIdeas = derived(
  [ideas, searchFilters],
  ([$ideas, $filters]) => {
    let filtered = [...$ideas];

    // Apply search filter
    if ($filters.search) {
      const searchTerm = $filters.search.toLowerCase().trim();
      filtered = filtered.filter(
        (idea) =>
          idea.title.toLowerCase().includes(searchTerm) ||
          idea.original_description.toLowerCase().includes(searchTerm) ||
          idea.tags.some((tag) => tag.toLowerCase().includes(searchTerm)),
      );
    }

    // Apply status filter
    if ($filters.status) {
      filtered = filtered.filter((idea) => idea.status === $filters.status);
    } else {
      // By default, exclude archived ideas unless explicitly showing them
      if (!$filters.includeArchived) {
        filtered = filtered.filter((idea) => idea.status !== "archived");
      }
    }

    // Apply tags filter
    if ($filters.tags && $filters.tags.length > 0) {
      filtered = filtered.filter(
        (idea) =>
          $filters.tags?.every((tag) => idea.tags.includes(tag)) ?? false,
      );
    }

    // Apply sorting
    filtered.sort((a, b) => {
      const field = $filters.sortBy || "updated_at";
      const order = $filters.sortOrder === "asc" ? 1 : -1;

      if (field === "title") {
        return order * a.title.localeCompare(b.title);
      } else {
        // Safe type-checked date field access
        const aValue = field === "created_at" ? a.created_at : a.updated_at;
        const bValue = field === "created_at" ? b.created_at : b.updated_at;
        const aDate = new Date(aValue);
        const bDate = new Date(bValue);
        return order * (aDate.getTime() - bDate.getTime());
      }
    });

    return filtered;
  },
);

export const ideasByStatus = derived(ideas, ($ideas) => {
  const byStatus: Record<string, Idea[]> = {
    captured: [],
    refining: [], // Updated from 'refined'
    planned: [], // Updated from 'building'
    archived: [], // Updated from 'completed'
  };

  $ideas.forEach((idea) => {
    byStatus[idea.status].push(idea);
  });

  return byStatus;
});

export const allTags = derived(ideas, ($ideas) => {
  const tagSet = new Set<string>();
  $ideas.forEach((idea) => {
    idea.tags.forEach((tag) => tagSet.add(tag));
  });
  return Array.from(tagSet).sort();
});

// New derived stores for progress tracking
export const refinementProgress = derived(
  [currentIdea, currentRefinementSession],
  ([$currentIdea, $currentSession]) => {
    if (!$currentIdea || !$currentSession) {
      return { current: 0, total: 0, percentage: 0 };
    }

    const total = $currentSession.questions.length;
    const current = Object.keys($currentSession.answers).length;
    const percentage = total > 0 ? Math.round((current / total) * 100) : 0;

    return { current, total, percentage };
  },
);

export const activePlan = derived(
  ideaPlans,
  ($plans) => $plans.find((plan) => plan.is_active) || null,
);

// ====================================
// IDEA ACTIONS
// ====================================

export const ideaActions = {
  async loadIdeas(filters?: SearchFilters): Promise<void> {
    ideasLoading.set(true);
    try {
      const loadedIdeas = await api.getIdeas({
        search: filters?.search,
        tags: filters?.tags,
        status: filters?.status,
        limit: 100,
      });
      ideas.set(loadedIdeas);
    } catch (error) {
      console.error("Failed to load ideas:", error);
      throw error;
    } finally {
      ideasLoading.set(false);
    }
  },

  async loadIdea(ideaId: string): Promise<IdeaDetail> {
    ideaLoading.set(true);
    try {
      const idea = await api.getIdea(ideaId);
      currentIdea.set(idea);
      return idea;
    } catch (error) {
      console.error("Failed to load idea:", error);
      throw error;
    } finally {
      ideaLoading.set(false);
    }
  },

  async createIdea(ideaData: {
    title: string;
    original_description: string;
    tags: string[];
  }): Promise<Idea> {
    try {
      const newIdea = await api.createIdea(ideaData);
      ideas.update((items) => [newIdea, ...items]);
      return newIdea;
    } catch (error) {
      console.error("Failed to create idea:", error);
      throw error;
    }
  },

  async updateIdea(ideaId: string, updates: Partial<Idea>): Promise<Idea> {
    try {
      const updatedIdea = await api.updateIdea(ideaId, updates);

      // Update in ideas list
      ideas.update((items) =>
        items.map((item) => (item.id === ideaId ? updatedIdea : item)),
      );

      // Update current idea if it matches
      currentIdea.update((current) =>
        current?.id === ideaId ? { ...current, ...updatedIdea } : current,
      );

      return updatedIdea;
    } catch (error) {
      console.error("Failed to update idea:", error);
      throw error;
    }
  },

  async deleteIdea(ideaId: string): Promise<void> {
    console.log("ideaActions.deleteIdea called with:", ideaId);
    try {
      console.log("Making API call to delete idea...");
      await api.deleteIdea(ideaId);
      console.log("API delete call successful, updating local state...");

      // Remove from ideas list
      ideas.update((items) => {
        const filteredItems = items.filter((item) => item.id !== ideaId);
        console.log(
          `Removed idea from local store. Before: ${items.length}, After: ${filteredItems.length}`,
        );
        return filteredItems;
      });

      // Clear current idea if it matches
      currentIdea.update((current) => {
        if (current?.id === ideaId) {
          console.log("Clearing current idea as it was deleted");
          return null;
        }
        return current;
      });

      console.log("Delete operation completed successfully");
    } catch (error) {
      console.error("Failed to delete idea in store:", error);
      console.error("API delete error details:", {
        message: error instanceof Error ? error.message : "Unknown error",
        name: error instanceof Error ? error.name : "Unknown",
        stack: error instanceof Error ? error.stack : undefined,
      });
      throw error;
    }
  },

  async loadStats(): Promise<IdeaStats> {
    try {
      const stats = await api.getIdeaStats();
      ideaStats.set(stats);
      return stats;
    } catch (error) {
      console.error("Failed to load idea stats:", error);
      throw error;
    }
  },

  async loadRecentIdeas(limit = 5): Promise<Idea[]> {
    try {
      const recent = await api.getRecentIdeas(limit);
      return recent;
    } catch (error) {
      console.error("Failed to load recent ideas:", error);
      throw error;
    }
  },

  async getIdeaSummary(ideaId: string): Promise<IdeaSummary> {
    try {
      const summary = await api.getIdeaSummary(ideaId);
      return summary;
    } catch (error) {
      console.error("Failed to load idea summary:", error);
      throw error;
    }
  },

  // Filter actions
  updateSearch(search: string) {
    searchFilters.update((filters) => ({ ...filters, search }));
  },

  updateStatusFilter(status: string) {
    searchFilters.update((filters) => ({ ...filters, status }));
  },

  updateTagsFilter(tags: string[]) {
    searchFilters.update((filters) => ({ ...filters, tags }));
  },

  updateSorting(
    sortBy: "created_at" | "updated_at" | "title",
    sortOrder: "asc" | "desc",
  ) {
    searchFilters.update((filters) => ({ ...filters, sortBy, sortOrder }));
  },

  updateFilters(updates: Partial<SearchFilters>) {
    searchFilters.update((filters) => ({ ...filters, ...updates }));
  },

  clearFilters() {
    searchFilters.set({
      search: "",
      tags: [],
      status: "",
      sortBy: "updated_at",
      sortOrder: "desc",
    });
  },
};

// ====================================
// REFINEMENT ACTIONS
// ====================================

export const refinementActions = {
  async createSession(ideaId: string): Promise<RefinementSession> {
    refinementLoading.set(true);
    try {
      const session = await api.createRefinementSession({ idea_id: ideaId });
      currentRefinementSession.set(session);
      return session;
    } catch (error) {
      console.error("Failed to create refinement session:", error);
      throw error;
    } finally {
      refinementLoading.set(false);
    }
  },

  async loadSession(sessionId: string): Promise<RefinementSession> {
    refinementLoading.set(true);
    try {
      const session = await api.getRefinementSession(sessionId);
      currentRefinementSession.set(session);
      return session;
    } catch (error) {
      console.error("Failed to load refinement session:", error);
      throw error;
    } finally {
      refinementLoading.set(false);
    }
  },

  async loadIdeaSessions(ideaId: string): Promise<RefinementSession[]> {
    try {
      const sessions = await api.getIdeaRefinementSessions(ideaId);
      refinementSessions.set(sessions);
      return sessions;
    } catch (error) {
      console.error("Failed to load idea refinement sessions:", error);
      throw error;
    }
  },

  async submitAnswers(
    sessionId: string,
    answers: Record<string, string>,
  ): Promise<RefinementSession> {
    try {
      const updatedSession = await api.submitRefinementAnswers(sessionId, {
        answers,
      });
      currentRefinementSession.set(updatedSession);

      // Update the idea if the session is complete
      if (updatedSession.is_complete) {
        const currentIdeaValue = get(currentIdea);
        if (currentIdeaValue) {
          await ideaActions.loadIdea(currentIdeaValue.id); // Refresh idea data
        }
      }

      return updatedSession;
    } catch (error) {
      console.error("Failed to submit refinement answers:", error);
      throw error;
    }
  },

  async completeSession(sessionId: string): Promise<RefinementSession> {
    try {
      const completedSession = await api.completeRefinementSession(sessionId);
      currentRefinementSession.set(completedSession);
      return completedSession;
    } catch (error) {
      console.error("Failed to complete refinement session:", error);
      throw error;
    }
  },
};

// ====================================
// PLAN ACTIONS
// ====================================

export const planActions = {
  async generatePlan(refinementSessionId: string): Promise<Plan> {
    planLoading.set(true);
    try {
      const plan = await api.generatePlan(refinementSessionId);
      currentPlan.set(plan);

      // Refresh idea plans
      const currentIdeaValue = get(currentIdea);
      if (currentIdeaValue) {
        await planActions.loadIdeaPlans(currentIdeaValue.id);
        await ideaActions.loadIdea(currentIdeaValue.id); // Refresh idea data
      }

      return plan;
    } catch (error) {
      console.error("Failed to generate plan:", error);
      throw error;
    } finally {
      planLoading.set(false);
    }
  },

  async loadPlan(planId: string): Promise<Plan> {
    planLoading.set(true);
    try {
      const plan = await api.getPlan(planId);
      currentPlan.set(plan);
      return plan;
    } catch (error) {
      console.error("Failed to load plan:", error);
      throw error;
    } finally {
      planLoading.set(false);
    }
  },

  async loadIdeaPlans(ideaId: string): Promise<Plan[]> {
    try {
      const plans = await api.getIdeaPlans(ideaId);
      ideaPlans.set(plans);
      return plans;
    } catch (error) {
      console.error("Failed to load idea plans:", error);
      throw error;
    }
  },

  async updatePlan(planId: string, updates: Partial<Plan>): Promise<Plan> {
    try {
      const updatedPlan = await api.updatePlan(planId, updates);
      currentPlan.update((current) =>
        current?.id === planId ? updatedPlan : current,
      );

      // Update in plans list
      ideaPlans.update((plans) =>
        plans.map((plan) => (plan.id === planId ? updatedPlan : plan)),
      );

      return updatedPlan;
    } catch (error) {
      console.error("Failed to update plan:", error);
      throw error;
    }
  },

  async activatePlan(planId: string): Promise<Plan> {
    try {
      const activatedPlan = await api.activatePlan(planId);

      // Update current plan
      currentPlan.set(activatedPlan);

      // Update plans list (deactivate others, activate this one)
      ideaPlans.update((plans) =>
        plans.map((plan) => ({
          ...plan,
          is_active: plan.id === planId,
        })),
      );

      return activatedPlan;
    } catch (error) {
      console.error("Failed to activate plan:", error);
      throw error;
    }
  },

  async deletePlan(planId: string): Promise<void> {
    try {
      await api.deletePlan(planId);

      // Remove from plans list
      ideaPlans.update((plans) => plans.filter((plan) => plan.id !== planId));

      // Clear current plan if it matches
      currentPlan.update((current) =>
        current?.id === planId ? null : current,
      );
    } catch (error) {
      console.error("Failed to delete plan:", error);
      throw error;
    }
  },

  async exportPlanJson(planId: string, filename?: string): Promise<void> {
    try {
      await api.downloadPlanJson(planId, filename);
    } catch (error) {
      console.error("Failed to export plan as JSON:", error);
      throw error;
    }
  },

  async exportPlanMarkdown(planId: string, filename?: string): Promise<void> {
    try {
      await api.downloadPlanMarkdown(planId, filename);
    } catch (error) {
      console.error("Failed to export plan as Markdown:", error);
      throw error;
    }
  },
};
