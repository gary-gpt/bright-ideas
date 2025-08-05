<script lang="ts">
  /**
   * Dashboard/Landing page
   */
  import { onMount } from 'svelte';
  import { Plus, TrendingUp, BookOpen, Clock } from 'lucide-svelte';
  import { ideaActions, ideas } from '$lib/stores';
  import { toastActions } from '$lib/stores';
  import Button from '$lib/components/shared/Button.svelte';
  import LoadingSpinner from '$lib/components/shared/LoadingSpinner.svelte';
  import type { Idea } from '$lib/types';

  let recentIdeas: Idea[] = [];
  let loading = true;
  let stats = {
    total_ideas: 0,
    status_counts: { captured: 0, refining: 0, planned: 0, archived: 0 },
    ideas_with_plans: 0,
    total_refinement_sessions: 0,
    completed_refinement_sessions: 0,
    average_sessions_per_idea: 0
  };

  onMount(async () => {
    try {
      // Load recent ideas and stats
      const [recent, ideaStats] = await Promise.all([
        ideaActions.loadRecentIdeas(5),
        ideaActions.loadStats()
      ]);
      
      recentIdeas = recent;
      stats = ideaStats;
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      toastActions.error('Failed to load dashboard data');
    } finally {
      loading = false;
    }
  });

  function getStatusColor(status: string): string {
    const colors = {
      captured: 'bg-blue-100 text-blue-800',
      refining: 'bg-yellow-100 text-yellow-800',
      planned: 'bg-green-100 text-green-800',
      archived: 'bg-gray-100 text-gray-800'
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  }

  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString([], {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
</script>

<svelte:head>
  <title>Dashboard - Bright Ideas</title>
</svelte:head>

<div class="p-6 max-w-7xl mx-auto">
  <!-- Header -->
  <div class="mb-8">
    <h1 class="text-3xl font-bold text-secondary-900 mb-2">
      Welcome to Bright Ideas
    </h1>
    <p class="text-lg text-secondary-600">
      Transform your vague concepts into actionable plans with AI assistance
    </p>
  </div>

  {#if loading}
    <div class="flex justify-center py-12">
      <LoadingSpinner size="lg" message="Loading dashboard..." />
    </div>
  {:else}
    <!-- Quick Actions -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      <div class="bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg p-6 text-white">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-semibold mb-2">Capture New Idea</h2>
            <p class="text-primary-100 mb-4">
              Start with a rough concept and let AI help you refine it
            </p>
            <Button variant="secondary" href="/capture">
              <Plus size={16} class="mr-2" />
              Get Started
            </Button>
          </div>
          <div class="hidden md:block">
            <Plus size={48} class="text-primary-200" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-secondary-200 p-6">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-semibold text-secondary-900 mb-2">Browse Ideas</h2>
            <p class="text-secondary-600 mb-4">
              Explore your saved ideas and continue building
            </p>
            <Button variant="outline" href="/ideas">
              <BookOpen size={16} class="mr-2" />
              View All Ideas
            </Button>
          </div>
          <div class="hidden md:block">
            <BookOpen size={48} class="text-secondary-300" />
          </div>
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-white rounded-lg border border-secondary-200 p-4">
        <div class="flex items-center">
          <div class="p-2 bg-blue-100 rounded-lg">
            <TrendingUp size={20} class="text-blue-600" />
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium text-secondary-600">Total Ideas</p>
            <p class="text-2xl font-bold text-secondary-900">{stats.total_ideas}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-secondary-200 p-4">
        <div class="flex items-center">
          <div class="p-2 bg-green-100 rounded-lg">
            <BookOpen size={20} class="text-green-600" />
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium text-secondary-600">Refining</p>
            <p class="text-2xl font-bold text-secondary-900">{stats.status_counts.refining}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-secondary-200 p-4">
        <div class="flex items-center">
          <div class="p-2 bg-yellow-100 rounded-lg">
            <Clock size={20} class="text-yellow-600" />
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium text-secondary-600">Planned</p>
            <p class="text-2xl font-bold text-secondary-900">{stats.status_counts.planned}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-secondary-200 p-4">
        <div class="flex items-center">
          <div class="p-2 bg-purple-100 rounded-lg">
            <TrendingUp size={20} class="text-purple-600" />
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium text-secondary-600">Archived</p>
            <p class="text-2xl font-bold text-secondary-900">{stats.status_counts.archived}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Ideas -->
    <div class="bg-white rounded-lg border border-secondary-200">
      <div class="p-6 border-b border-secondary-200">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-secondary-900">Recent Ideas</h2>
          <Button variant="ghost" size="sm" href="/ideas">
            View All
          </Button>
        </div>
      </div>

      {#if recentIdeas.length === 0}
        <div class="p-6 text-center">
          <div class="text-secondary-400 mb-4">
            <BookOpen size={48} class="mx-auto" />
          </div>
          <h3 class="text-lg font-medium text-secondary-900 mb-2">No ideas yet</h3>
          <p class="text-secondary-600 mb-4">
            Start by capturing your first idea
          </p>
          <Button href="/capture">
            <Plus size={16} class="mr-2" />
            Capture Idea
          </Button>
        </div>
      {:else}
        <div class="divide-y divide-secondary-200">
          {#each recentIdeas as idea}
            <div class="p-6 hover:bg-secondary-50 transition-colors">
              <div class="flex items-start justify-between">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center space-x-3 mb-2">
                    <h3 class="text-lg font-medium text-secondary-900 truncate">
                      <a href="/ideas/{idea.id}" class="hover:text-primary-600">
                        {idea.title}
                      </a>
                    </h3>
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getStatusColor(idea.status)}">
                      {idea.status}
                    </span>
                  </div>
                  <p class="text-secondary-600 mb-3 line-clamp-2">
                    {idea.original_description}
                  </p>
                  <div class="flex items-center justify-between">
                    <div class="flex flex-wrap gap-2">
                      {#each idea.tags.slice(0, 3) as tag}
                        <span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-secondary-100 text-secondary-700">
                          {tag}
                        </span>
                      {/each}
                      {#if idea.tags.length > 3}
                        <span class="text-xs text-secondary-500">
                          +{idea.tags.length - 3} more
                        </span>
                      {/if}
                    </div>
                    <span class="text-xs text-secondary-500">
                      {formatDate(idea.updated_at)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</div>