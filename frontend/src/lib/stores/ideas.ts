/**
 * Svelte stores for idea management
 */
import { writable, derived } from 'svelte/store';
import type { Idea, IdeaStats, SearchFilters } from '$lib/types';
import { api } from '$lib/services/api';

// Ideas store
export const ideas = writable<Idea[]>([]);
export const currentIdea = writable<Idea | null>(null);
export const ideaStats = writable<IdeaStats | null>(null);

// Search and filter store
export const searchFilters = writable<SearchFilters>({
  search: '',
  tags: [],
  status: '',
  sortBy: 'updated_at',
  sortOrder: 'desc'
});

// Loading states
export const ideasLoading = writable(false);
export const ideaLoading = writable(false);

// Derived stores
export const filteredIdeas = derived(
  [ideas, searchFilters],
  ([$ideas, $filters]) => {
    let filtered = [...$ideas];

    // Apply search filter
    if ($filters.search) {
      const searchTerm = $filters.search.toLowerCase();
      filtered = filtered.filter(idea => 
        idea.title.toLowerCase().includes(searchTerm) ||
        idea.original_description.toLowerCase().includes(searchTerm) ||
        (idea.refined_description && idea.refined_description.toLowerCase().includes(searchTerm))
      );
    }

    // Apply status filter
    if ($filters.status) {
      filtered = filtered.filter(idea => idea.status === $filters.status);
    }

    // Apply tags filter
    if ($filters.tags && $filters.tags.length > 0) {
      filtered = filtered.filter(idea => 
        $filters.tags!.every(tag => idea.tags.includes(tag))
      );
    }

    // Apply sorting
    filtered.sort((a, b) => {
      const field = $filters.sortBy || 'updated_at';
      const order = $filters.sortOrder === 'asc' ? 1 : -1;
      
      if (field === 'title') {
        return order * a.title.localeCompare(b.title);
      } else {
        const aDate = new Date(a[field as keyof Idea] as string);
        const bDate = new Date(b[field as keyof Idea] as string);
        return order * (aDate.getTime() - bDate.getTime());
      }
    });

    return filtered;
  }
);

export const ideasByStatus = derived(
  ideas,
  ($ideas) => {
    const byStatus: Record<string, Idea[]> = {
      captured: [],
      refined: [],
      building: [],
      completed: []
    };

    $ideas.forEach(idea => {
      byStatus[idea.status].push(idea);
    });

    return byStatus;
  }
);

export const allTags = derived(
  ideas,
  ($ideas) => {
    const tagSet = new Set<string>();
    $ideas.forEach(idea => {
      idea.tags.forEach(tag => tagSet.add(tag));
    });
    return Array.from(tagSet).sort();
  }
);

// Actions
export const ideaActions = {
  async loadIdeas(filters?: SearchFilters) {
    ideasLoading.set(true);
    try {
      const loadedIdeas = await api.getIdeas({
        search: filters?.search,
        tags: filters?.tags,
        status: filters?.status,
        limit: 100
      });
      ideas.set(loadedIdeas);
    } catch (error) {
      console.error('Failed to load ideas:', error);
      throw error;
    } finally {
      ideasLoading.set(false);
    }
  },

  async loadIdea(ideaId: string) {
    ideaLoading.set(true);
    try {
      const idea = await api.getIdea(ideaId);
      currentIdea.set(idea);
      return idea;
    } catch (error) {
      console.error('Failed to load idea:', error);
      throw error;
    } finally {
      ideaLoading.set(false);
    }
  },

  async createIdea(ideaData: { title: string; original_description: string; tags: string[] }) {
    try {
      const newIdea = await api.createIdea(ideaData);
      ideas.update(items => [newIdea, ...items]);
      return newIdea;
    } catch (error) {
      console.error('Failed to create idea:', error);
      throw error;
    }
  },

  async updateIdea(ideaId: string, updates: Partial<Idea>) {
    try {
      const updatedIdea = await api.updateIdea(ideaId, updates);
      
      // Update in ideas list
      ideas.update(items => 
        items.map(item => item.id === ideaId ? updatedIdea : item)
      );
      
      // Update current idea if it matches
      currentIdea.update(current => 
        current?.id === ideaId ? updatedIdea : current
      );
      
      return updatedIdea;
    } catch (error) {
      console.error('Failed to update idea:', error);
      throw error;
    }
  },

  async deleteIdea(ideaId: string) {
    try {
      await api.deleteIdea(ideaId);
      
      // Remove from ideas list
      ideas.update(items => items.filter(item => item.id !== ideaId));
      
      // Clear current idea if it matches
      currentIdea.update(current => 
        current?.id === ideaId ? null : current
      );
    } catch (error) {
      console.error('Failed to delete idea:', error);
      throw error;
    }
  },

  async loadStats() {
    try {
      const stats = await api.getIdeaStats();
      ideaStats.set(stats);
      return stats;
    } catch (error) {
      console.error('Failed to load idea stats:', error);
      throw error;
    }
  },

  async loadRecentIdeas(limit = 5) {
    try {
      const recent = await api.getRecentIdeas(limit);
      return recent;
    } catch (error) {
      console.error('Failed to load recent ideas:', error);
      throw error;
    }
  },

  // Filter actions
  updateSearch(search: string) {
    searchFilters.update(filters => ({ ...filters, search }));
  },

  updateStatusFilter(status: string) {
    searchFilters.update(filters => ({ ...filters, status }));
  },

  updateTagsFilter(tags: string[]) {
    searchFilters.update(filters => ({ ...filters, tags }));
  },

  updateSorting(sortBy: 'created_at' | 'updated_at' | 'title', sortOrder: 'asc' | 'desc') {
    searchFilters.update(filters => ({ ...filters, sortBy, sortOrder }));
  },

  clearFilters() {
    searchFilters.set({
      search: '',
      tags: [],
      status: '',
      sortBy: 'updated_at',
      sortOrder: 'desc'
    });
  }
};