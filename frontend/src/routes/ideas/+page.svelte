<script lang="ts">
  /**
   * Ideas library page with search and filtering
   */
  import { onMount } from 'svelte';
  import { Search, Filter, Plus, Grid, List } from 'lucide-svelte';
  import { ideaActions, filteredIdeas, allTags, searchFilters } from '$lib/stores';
  import { toastActions } from '$lib/stores';
  import Button from '$lib/components/shared/Button.svelte';
  import LoadingSpinner from '$lib/components/shared/LoadingSpinner.svelte';
  import type { Idea } from '$lib/types';

  let loading = true;
  let viewMode: 'grid' | 'list' = 'grid';
  let showFilters = false;

  onMount(async () => {
    try {
      await ideaActions.loadIdeas();
    } catch (error) {
      console.error('Failed to load ideas:', error);
      toastActions.error('Failed to load ideas');
    } finally {
      loading = false;
    }
  });

  function getStatusColor(status: string): string {
    const colors = {
      captured: 'bg-blue-100 text-blue-800 border-blue-200',
      refining: 'bg-yellow-100 text-yellow-800 border-yellow-200', // Updated from 'refined'
      planned: 'bg-green-100 text-green-800 border-green-200',     // Updated from 'building'
      archived: 'bg-gray-100 text-gray-800 border-gray-200'        // Updated from 'completed'
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800 border-gray-200';
  }

  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString([], {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  }

  function toggleTag(tag: string) {
    const currentTags = $searchFilters.tags || [];
    if (currentTags.includes(tag)) {
      ideaActions.updateTagsFilter(currentTags.filter(t => t !== tag));
    } else {
      ideaActions.updateTagsFilter([...currentTags, tag]);
    }
  }

  function clearFilters() {
    ideaActions.clearFilters();
    showFilters = false;
  }

  $: hasActiveFilters = $searchFilters.search || 
                      ($searchFilters.tags && $searchFilters.tags.length > 0) || 
                      $searchFilters.status;
</script>

<svelte:head>
  <title>Ideas Library - Bright Ideas</title>
  <meta name="description" content="Browse and manage your captured ideas" />
</svelte:head>

<div class="p-6 max-w-7xl mx-auto">
  <!-- Header -->
  <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
    <div>
      <h1 class="text-2xl font-bold text-secondary-900 mb-1">Ideas Library</h1>
      <p class="text-secondary-600">
        Browse and manage your captured ideas ({$filteredIdeas.length} ideas)
      </p>
    </div>
    <div class="flex items-center space-x-3 mt-4 sm:mt-0">
      <Button href="/capture">
        <Plus size={16} class="mr-2" />
        New Idea
      </Button>
    </div>
  </div>

  <!-- Search and Filters -->
  <div class="bg-white rounded-lg border border-secondary-200 p-4 mb-6">
    <div class="flex flex-col lg:flex-row lg:items-center space-y-4 lg:space-y-0 lg:space-x-4">
      <!-- Search -->
      <div class="flex-1 relative">
        <Search size={20} class="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400" />
        <input
          type="text"
          placeholder="Search ideas..."
          class="w-full pl-10 pr-4 py-2 border border-secondary-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
          bind:value={$searchFilters.search}
          on:input={(e) => ideaActions.updateSearch(e.currentTarget.value)}
        />
      </div>

      <!-- Archive Toggle -->
      <label class="flex items-center space-x-2">
        <input
          type="checkbox"
          class="rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
          bind:checked={$searchFilters.includeArchived}
          on:change={(e) => ideaActions.updateFilters({ includeArchived: e.currentTarget.checked })}
        />
        <span class="text-sm text-secondary-700">Include Archived</span>
      </label>

      <!-- View Toggle -->
      <div class="flex items-center bg-secondary-100 rounded-lg p-1">
        <button
          type="button"
          class="p-2 rounded-md {viewMode === 'grid' ? 'bg-white shadow-sm' : ''}"
          on:click={() => viewMode = 'grid'}
        >
          <Grid size={16} class="text-secondary-600" />
        </button>
        <button
          type="button"
          class="p-2 rounded-md {viewMode === 'list' ? 'bg-white shadow-sm' : ''}"
          on:click={() => viewMode = 'list'}
        >
          <List size={16} class="text-secondary-600" />
        </button>
      </div>

      <!-- Filter Toggle -->
      <Button
        variant="outline"
        on:click={() => showFilters = !showFilters}
      >
        <Filter size={16} class="mr-2" />
        Filters
        {#if hasActiveFilters}
          <span class="ml-2 inline-flex items-center justify-center w-2 h-2 bg-primary-600 rounded-full" />
        {/if}
      </Button>
    </div>

    <!-- Filter Panel -->
    {#if showFilters}
      <div class="mt-4 pt-4 border-t border-secondary-200">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- Status Filter -->
          <div>
            <label class="block text-sm font-medium text-secondary-700 mb-2">Status</label>
            <select
              class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
              bind:value={$searchFilters.status}
              on:change={(e) => ideaActions.updateStatusFilter(e.currentTarget.value)}
            >
              <option value="">All statuses</option>
              <option value="captured">Captured</option>
              <option value="refining">Refining</option>
              <option value="planned">Planned</option>
              <option value="archived">Archived</option>
            </select>
          </div>

          <!-- Tags Filter -->
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-secondary-700 mb-2">Tags</label>
            <div class="flex flex-wrap gap-2 max-h-24 overflow-y-auto">
              {#each $allTags as tag}
                <button
                  type="button"
                  class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border transition-colors
                    {($searchFilters.tags || []).includes(tag)
                      ? 'bg-primary-100 text-primary-800 border-primary-200'
                      : 'bg-secondary-100 text-secondary-700 border-secondary-200 hover:bg-secondary-200'}"
                  on:click={() => toggleTag(tag)}
                >
                  {tag}
                </button>
              {/each}
            </div>
          </div>
        </div>

        <!-- Clear Filters -->
        {#if hasActiveFilters}
          <div class="mt-4 flex justify-end">
            <Button variant="ghost" size="sm" on:click={clearFilters}>
              Clear Filters
            </Button>
          </div>
        {/if}
      </div>
    {/if}
  </div>

  <!-- Ideas Grid/List -->
  {#if loading}
    <div class="flex justify-center py-12">
      <LoadingSpinner size="lg" message="Loading ideas..." />
    </div>
  {:else if $filteredIdeas.length === 0}
    <div class="text-center py-12">
      <div class="text-secondary-400 mb-4">
        <Search size={48} class="mx-auto" />
      </div>
      <h3 class="text-lg font-medium text-secondary-900 mb-2">
        {hasActiveFilters ? 'No ideas match your filters' : 'No ideas yet'}
      </h3>
      <p class="text-secondary-600 mb-4">
        {hasActiveFilters 
          ? 'Try adjusting your search or filters' 
          : 'Start by capturing your first idea'}
      </p>
      {#if hasActiveFilters}
        <Button variant="outline" on:click={clearFilters}>
          Clear Filters
        </Button>
      {:else}
        <Button href="/capture">
          <Plus size={16} class="mr-2" />
          Capture Idea
        </Button>
      {/if}
    </div>
  {:else}
    <div class="{viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'}">
      {#each $filteredIdeas as idea (idea.id)}
        {#if viewMode === 'grid'}
          <!-- Grid Card View -->
          <div class="bg-white rounded-lg border border-secondary-200 hover:shadow-md transition-shadow">
            <div class="p-6">
              <div class="flex items-start justify-between mb-3">
                <h3 class="text-lg font-semibold text-secondary-900 line-clamp-2">
                  <a href="/ideas/{idea.id}" class="hover:text-primary-600">
                    {idea.title}
                  </a>
                </h3>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border {getStatusColor(idea.status)}">
                  {idea.status}
                </span>
              </div>
              
              <p class="text-secondary-600 text-sm mb-4 line-clamp-3">
                {idea.original_description}
              </p>
              
              <div class="flex flex-wrap gap-2 mb-4">
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
              
              <div class="flex items-center justify-between text-xs text-secondary-500">
                <span>Updated {formatDate(idea.updated_at)}</span>
                <a href="/ideas/{idea.id}" class="text-primary-600 hover:text-primary-700 font-medium">
                  View Details →
                </a>
              </div>
            </div>
          </div>
        {:else}
          <!-- List Row View -->
          <div class="bg-white rounded-lg border border-secondary-200 hover:shadow-sm transition-shadow">
            <div class="p-6">
              <div class="flex items-start justify-between">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center space-x-3 mb-2">
                    <h3 class="text-lg font-semibold text-secondary-900 truncate">
                      <a href="/ideas/{idea.id}" class="hover:text-primary-600">
                        {idea.title}
                      </a>
                    </h3>
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border {getStatusColor(idea.status)}">
                      {idea.status}
                    </span>
                  </div>
                  
                  <p class="text-secondary-600 mb-3 line-clamp-2">
                    {idea.original_description}
                  </p>
                  
                  <div class="flex items-center justify-between">
                    <div class="flex flex-wrap gap-2">
                      {#each idea.tags.slice(0, 4) as tag}
                        <span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-secondary-100 text-secondary-700">
                          {tag}
                        </span>
                      {/each}
                      {#if idea.tags.length > 4}
                        <span class="text-xs text-secondary-500">
                          +{idea.tags.length - 4} more
                        </span>
                      {/if}
                    </div>
                    <span class="text-xs text-secondary-500 whitespace-nowrap">
                      Updated {formatDate(idea.updated_at)}
                    </span>
                  </div>
                </div>
                
                <div class="ml-6 flex-shrink-0">
                  <a href="/ideas/{idea.id}" class="text-primary-600 hover:text-primary-700 font-medium text-sm">
                    View Details →
                  </a>
                </div>
              </div>
            </div>
          </div>
        {/if}
      {/each}
    </div>
  {/if}
</div>