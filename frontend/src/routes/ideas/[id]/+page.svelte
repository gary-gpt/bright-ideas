<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { ideaActions } from '$lib/stores';
  import { toastActions } from '$lib/stores';
  import Button from '$lib/components/shared/Button.svelte';
  import LoadingSpinner from '$lib/components/shared/LoadingSpinner.svelte';
  import type { Idea } from '$lib/types';

  let idea: Idea | null = null;
  let loading = true;
  let refining = false;

  $: ideaId = $page.params.id;

  onMount(async () => {
    if (ideaId) {
      try {
        idea = await ideaActions.loadIdea(ideaId);
      } catch (error) {
        console.error('Failed to load idea:', error);
        toastActions.error('Failed to load idea');
        goto('/ideas');
      } finally {
        loading = false;
      }
    }
  });

  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString([], {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  function getStatusColor(status: string): string {
    const colors = {
      captured: 'bg-blue-100 text-blue-800 border-blue-200',
      refined: 'bg-green-100 text-green-800 border-green-200',
      building: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      completed: 'bg-purple-100 text-purple-800 border-purple-200'
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800 border-gray-200';
  }

  async function startRefinement() {
    if (!idea) return;
    
    refining = true;
    try {
      // This will trigger AI refinement process
      goto(`/ideas/${idea.id}/refine`);
    } catch (error) {
      console.error('Failed to start refinement:', error);
      toastActions.error('Failed to start refinement');
    } finally {
      refining = false;
    }
  }
</script>

<svelte:head>
  <title>{idea ? idea.title : 'Loading...'} - Bright Ideas</title>
  <meta name="description" content={idea ? idea.original_description : 'Idea details'} />
</svelte:head>

<div class="min-h-screen bg-secondary-50 py-8">
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Back Navigation -->
    <div class="mb-6">
      <Button variant="ghost" href="/ideas" size="sm">
        ← Back to Ideas
      </Button>
    </div>

    {#if loading}
      <div class="flex justify-center py-12">
        <LoadingSpinner size="lg" message="Loading idea details..." />
      </div>
    {:else if idea}
      <!-- Idea Header -->
      <div class="bg-white rounded-lg shadow-sm border border-secondary-200 mb-6">
        <div class="p-6">
          <div class="flex items-start justify-between mb-4">
            <div class="flex-1">
              <h1 class="text-3xl font-bold text-secondary-900 mb-2">
                {idea.title}
              </h1>
              <div class="flex items-center space-x-4">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border {getStatusColor(idea.status)}">
                  {idea.status}
                </span>
                <span class="text-sm text-secondary-500">
                  Created {formatDate(idea.created_at)}
                </span>
                <span class="text-sm text-secondary-500">
                  Updated {formatDate(idea.updated_at)}
                </span>
              </div>
            </div>
          </div>

          <!-- Tags -->
          {#if idea.tags.length > 0}
            <div class="flex flex-wrap gap-2 mb-4">
              {#each idea.tags as tag}
                <span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-secondary-100 text-secondary-700">
                  {tag}
                </span>
              {/each}
            </div>
          {/if}

          <!-- Action Buttons -->
          <div class="flex space-x-3">
            <Button on:click={startRefinement} loading={refining} disabled={refining}>
              {idea.status === 'captured' ? 'Start AI Refinement' : 'Continue Refinement'}
            </Button>
            <Button variant="outline" href="/ideas/{idea.id}/edit">
              Edit Details
            </Button>
          </div>
        </div>
      </div>

      <!-- Content Sections -->
      <div class="space-y-6">
        <!-- Original Description -->
        <div class="bg-white rounded-lg shadow-sm border border-secondary-200">
          <div class="p-6">
            <h2 class="text-lg font-semibold text-secondary-900 mb-3">Original Idea</h2>
            <div class="prose prose-sm max-w-none text-secondary-700">
              <p>{idea.original_description}</p>
            </div>
          </div>
        </div>

        <!-- Refined Description (if exists) -->
        {#if idea.refined_description}
          <div class="bg-white rounded-lg shadow-sm border border-secondary-200">
            <div class="p-6">
              <h2 class="text-lg font-semibold text-secondary-900 mb-3">AI-Refined Description</h2>
              <div class="prose prose-sm max-w-none text-secondary-700">
                <p>{idea.refined_description}</p>
              </div>
            </div>
          </div>
        {/if}

        <!-- Problem Statement (if exists) -->
        {#if idea.problem_statement}
          <div class="bg-white rounded-lg shadow-sm border border-secondary-200">
            <div class="p-6">
              <h2 class="text-lg font-semibold text-secondary-900 mb-3">Problem Statement</h2>
              <div class="prose prose-sm max-w-none text-secondary-700">
                <p>{idea.problem_statement}</p>
              </div>
            </div>
          </div>
        {/if}

        <!-- Target Audience (if exists) -->
        {#if idea.target_audience}
          <div class="bg-white rounded-lg shadow-sm border border-secondary-200">
            <div class="p-6">
              <h2 class="text-lg font-semibold text-secondary-900 mb-3">Target Audience</h2>
              <div class="prose prose-sm max-w-none text-secondary-700">
                <p>{idea.target_audience}</p>
              </div>
            </div>
          </div>
        {/if}

        <!-- Implementation Notes (if exists) -->
        {#if idea.implementation_notes && Object.keys(idea.implementation_notes).length > 0}
          <div class="bg-white rounded-lg shadow-sm border border-secondary-200">
            <div class="p-6">
              <h2 class="text-lg font-semibold text-secondary-900 mb-3">Implementation Notes</h2>
              <div class="prose prose-sm max-w-none text-secondary-700">
                <pre class="whitespace-pre-wrap">{JSON.stringify(idea.implementation_notes, null, 2)}</pre>
              </div>
            </div>
          </div>
        {/if}
      </div>
    {:else}
      <div class="text-center py-12">
        <h1 class="text-2xl font-bold text-secondary-900 mb-2">Idea Not Found</h1>
        <p class="text-secondary-600 mb-4">The idea you're looking for doesn't exist or has been deleted.</p>
        <Button href="/ideas">Back to Ideas</Button>
      </div>
    {/if}
  </div>
</div>