<script lang="ts">
  /**
   * Archived ideas view - shows only archived ideas with restore functionality
   */
  import { onMount } from 'svelte';
  import { Archive, RotateCcw, Trash2 } from 'lucide-svelte';
  import { ideaActions, ideas } from '$lib/stores';
  import { toastActions } from '$lib/stores';
  import Button from '$lib/components/shared/Button.svelte';
  import LoadingSpinner from '$lib/components/shared/LoadingSpinner.svelte';
  import type { Idea } from '$lib/types';

  let loading = true;
  let archivedIdeas: Idea[] = [];

  onMount(async () => {
    try {
      await ideaActions.loadIdeas();
      // Filter for archived ideas
      ideas.subscribe(allIdeas => {
        archivedIdeas = allIdeas.filter(idea => idea.status === 'archived');
      });
    } catch (error) {
      console.error('Failed to load archived ideas:', error);
      toastActions.error('Failed to load archived ideas');
    } finally {
      loading = false;
    }
  });

  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString([], {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  }

  async function restoreIdea(idea: Idea) {
    if (confirm(`Restore "${idea.title}" to active ideas?`)) {
      try {
        await ideaActions.updateIdea(idea.id, { status: 'captured' });
        toastActions.success('Idea restored successfully');
        // Refresh the list
        await ideaActions.loadIdeas();
      } catch (error) {
        console.error('Failed to restore idea:', error);
        toastActions.error('Failed to restore idea');
      }
    }
  }

  async function deleteIdea(idea: Idea) {
    if (confirm(`Permanently delete "${idea.title}"? This action cannot be undone.`)) {
      try {
        await ideaActions.deleteIdea(idea.id);
        toastActions.success('Idea deleted permanently');
        // Refresh the list
        await ideaActions.loadIdeas();
      } catch (error) {
        console.error('Failed to delete idea:', error);
        toastActions.error('Failed to delete idea');
      }
    }
  }
</script>

<svelte:head>
  <title>Archived Ideas - Bright Ideas</title>
  <meta name="description" content="View and manage your archived ideas" />
</svelte:head>

<div class="min-h-screen bg-secondary-50 py-8">
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
      <div>
        <h1 class="text-3xl font-bold text-secondary-900 mb-2">
          <Archive size={32} class="inline mr-3" />
          Archived Ideas
        </h1>
        <p class="text-secondary-600">
          Manage your archived ideas ({archivedIdeas.length} archived)
        </p>
      </div>
      <div class="flex items-center space-x-3 mt-4 sm:mt-0">
        <Button href="/ideas" variant="outline">
          ← Back to Library
        </Button>
      </div>
    </div>

    {#if loading}
      <div class="flex justify-center py-12">
        <LoadingSpinner size="lg" message="Loading archived ideas..." />
      </div>
    {:else if archivedIdeas.length === 0}
      <div class="text-center py-12">
        <Archive size={64} class="mx-auto text-secondary-400 mb-4" />
        <h2 class="text-xl font-semibold text-secondary-900 mb-2">No Archived Ideas</h2>
        <p class="text-secondary-600 mb-4">You haven't archived any ideas yet.</p>
        <Button href="/ideas">Browse Active Ideas</Button>
      </div>
    {:else}
      <!-- Archived Ideas Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each archivedIdeas as idea}
          <div class="bg-white rounded-lg border border-secondary-200 shadow-sm hover:shadow-md transition-shadow">
            <div class="p-6">
              <!-- Header -->
              <div class="flex items-start justify-between mb-3">
                <h3 class="text-lg font-semibold text-secondary-900 line-clamp-2">
                  <a href="/ideas/{idea.id}" class="hover:text-primary-600 transition-colors">
                    {idea.title}
                  </a>
                </h3>
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 border border-gray-200">
                  Archived
                </span>
              </div>

              <!-- Description -->
              <p class="text-secondary-600 text-sm mb-4 line-clamp-3">
                {idea.original_description}
              </p>

              <!-- Tags -->
              {#if idea.tags && idea.tags.length > 0}
                <div class="flex flex-wrap gap-1 mb-4">
                  {#each idea.tags.slice(0, 3) as tag}
                    <span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-secondary-100 text-secondary-700">
                      {tag}
                    </span>
                  {/each}
                  {#if idea.tags.length > 3}
                    <span class="text-xs text-secondary-500">+{idea.tags.length - 3} more</span>
                  {/if}
                </div>
              {/if}

              <!-- Footer -->
              <div class="border-t border-secondary-200 pt-4">
                <div class="flex items-center justify-between text-sm text-secondary-500 mb-3">
                  <span>Archived {formatDate(idea.updated_at)}</span>
                </div>
                
                <!-- Actions -->
                <div class="flex space-x-2">
                  <Button size="sm" variant="outline" on:click={() => restoreIdea(idea)}>
                    <RotateCcw size={14} class="mr-1" />
                    Restore
                  </Button>
                  <Button size="sm" variant="outline" on:click={() => deleteIdea(idea)}>
                    <Trash2 size={14} class="mr-1" />
                    Delete
                  </Button>
                </div>
              </div>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>