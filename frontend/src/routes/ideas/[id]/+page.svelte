<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { ideaActions, planActions, currentIdea } from '$lib/stores';
  import { toastActions } from '$lib/stores';
  import Button from '$lib/components/shared/Button.svelte';
  import LoadingSpinner from '$lib/components/shared/LoadingSpinner.svelte';
  import type { IdeaDetail, Plan } from '$lib/types';

  let idea: IdeaDetail | null = null;
  let ideaPlans: Plan[] = [];
  let loading = true;
  let plansLoading = false;

  $: ideaId = $page.params.id;

  onMount(async () => {
    if (ideaId) {
      try {
        // Load idea details and plans in parallel
        const [loadedIdea, loadedPlans] = await Promise.all([
          ideaActions.loadIdea(ideaId),
          planActions.loadIdeaPlans(ideaId).catch(() => []) // Don't fail if plans can't load
        ]);
        
        idea = loadedIdea;
        ideaPlans = loadedPlans;
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
      refining: 'bg-yellow-100 text-yellow-800 border-yellow-200', // Updated from 'refined'
      planned: 'bg-green-100 text-green-800 border-green-200',     // Updated from 'building'
      archived: 'bg-gray-100 text-gray-800 border-gray-200'        // Updated from 'completed'
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800 border-gray-200';
  }

  function getStatusText(status: string): string {
    const statusTexts = {
      captured: 'Ready for Refinement',
      refining: 'In Refinement',
      planned: 'Implementation Planned',
      archived: 'Archived'
    };
    return statusTexts[status as keyof typeof statusTexts] || status;
  }

  function startRefinement() {
    if (!idea) return;
    goto(`/ideas/${idea.id}/refine`);
  }

  function viewPlans() {
    if (!idea) return;
    goto(`/ideas/${idea.id}/plans`);
  }

  async function archiveIdea() {
    if (!idea) return;
    
    if (confirm(`Archive "${idea.title}"? This will mark it as archived but not delete it.`)) {
      loading = true;
      try {
        await ideaActions.updateIdea(idea.id, { status: 'archived' });
        toastActions.success('Idea archived successfully');
        // Refresh the idea data
        idea = await ideaActions.loadIdea(ideaId);
      } catch (error) {
        console.error('Failed to archive idea:', error);
        toastActions.error('Failed to archive idea');
      } finally {
        loading = false;
      }
    }
  }

  async function deleteIdea() {
    if (!idea) return;
    
    if (confirm(`Delete "${idea.title}"? This action cannot be undone.`)) {
      loading = true;
      try {
        await ideaActions.deleteIdea(idea.id);
        toastActions.success('Idea deleted successfully');
        goto('/ideas');
      } catch (error) {
        console.error('Failed to delete idea:', error);
        toastActions.error('Failed to delete idea');
        loading = false;
      }
    }
  }

  function getNextStepAction() {
    if (!idea) return null;
    
    switch (idea.status) {
      case 'captured':
        return { text: 'Start AI Refinement', action: startRefinement };
      case 'refining':
        return { text: 'Continue Refinement', action: startRefinement };
      case 'planned':
        return idea.has_active_plan 
          ? { text: 'View Implementation Plan', action: viewPlans }
          : { text: 'Select Implementation Plan', action: viewPlans };
      default:
        return null;
    }
  }

  $: nextStep = getNextStepAction();
  $: activePlan = ideaPlans.find(plan => plan.is_active);
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
              <div class="flex items-center space-x-4 mb-4">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border {getStatusColor(idea.status)}">
                  {getStatusText(idea.status)}
                </span>
                <span class="text-sm text-secondary-500">
                  Created {formatDate(idea.created_at)}
                </span>
                <span class="text-sm text-secondary-500">
                  Updated {formatDate(idea.updated_at)}
                </span>
              </div>

              <!-- Progress Indicators -->
              <div class="grid grid-cols-3 gap-4 mb-4">
                <div class="text-center p-3 bg-secondary-50 rounded-lg">
                  <div class="text-lg font-semibold text-secondary-900">{idea.refinement_sessions_count}</div>
                  <div class="text-xs text-secondary-600">Refinement Sessions</div>
                </div>
                <div class="text-center p-3 bg-secondary-50 rounded-lg">
                  <div class="text-lg font-semibold text-secondary-900">{idea.plans_count}</div>
                  <div class="text-xs text-secondary-600">Implementation Plans</div>
                </div>
                <div class="text-center p-3 bg-secondary-50 rounded-lg">
                  <div class="text-lg font-semibold {idea.has_active_plan ? 'text-green-600' : 'text-secondary-400'}">
                    {idea.has_active_plan ? '✓' : '○'}
                  </div>
                  <div class="text-xs text-secondary-600">Active Plan</div>
                </div>
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
            {#if nextStep}
              <Button on:click={nextStep.action}>
                {nextStep.text}
              </Button>
            {:else}
              <!-- Fallback refinement button for any status -->
              <Button on:click={startRefinement}>
                Start Refinement
              </Button>
            {/if}
            
            {#if idea.plans_count > 0}
              <Button variant="outline" on:click={viewPlans}>
                View All Plans ({idea.plans_count})
              </Button>
            {/if}
            
            <!-- Archive/Delete Actions -->
            {#if idea.status !== 'archived'}
              <Button variant="outline" on:click={archiveIdea}>
                Archive
              </Button>
            {/if}
            
            <Button variant="outline" on:click={deleteIdea}>
              Delete
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
              <p class="whitespace-pre-wrap">{idea.original_description}</p>
            </div>
          </div>
        </div>

        <!-- Active Plan Summary -->
        {#if activePlan}
          <div class="bg-green-50 rounded-lg border border-green-200">
            <div class="p-6">
              <div class="flex items-center justify-between mb-3">
                <h2 class="text-lg font-semibold text-green-900">Active Implementation Plan</h2>
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  {activePlan.status}
                </span>
              </div>
              <div class="prose prose-sm max-w-none text-green-800 mb-4">
                <p>{activePlan.summary}</p>
              </div>
              <div class="flex items-center space-x-3 text-sm text-green-700">
                <span>{activePlan.steps.length} steps</span>
                <span>•</span>
                <span>{activePlan.resources.length} resources</span>
                <span>•</span>
                <span>Created {formatDate(activePlan.created_at)}</span>
              </div>
              <div class="mt-4 flex space-x-2">
                <Button size="sm" href="/ideas/{idea.id}/plans/{activePlan.id}">
                  View Full Plan
                </Button>
                <Button size="sm" variant="outline" on:click={() => planActions.exportPlanMarkdown(activePlan.id, `${idea.title}_plan.md`)}>
                  Export Plan
                </Button>
              </div>
            </div>
          </div>
        {/if}

        <!-- Latest Refinement Session -->
        {#if idea.latest_session}
          <div class="bg-white rounded-lg shadow-sm border border-secondary-200">
            <div class="p-6">
              <div class="flex items-center justify-between mb-3">
                <h2 class="text-lg font-semibold text-secondary-900">Latest Refinement Session</h2>
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium {idea.latest_session.is_complete ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}">
                  {idea.latest_session.is_complete ? 'Complete' : 'In Progress'}
                </span>
              </div>
              <div class="text-sm text-secondary-600 mb-3">
                {Object.keys(idea.latest_session.answers).length} of {idea.latest_session.questions.length} questions answered
              </div>
              <div class="w-full bg-secondary-200 rounded-full h-2 mb-4">
                <div 
                  class="bg-primary-600 h-2 rounded-full transition-all duration-300" 
                  style="width: {Math.round((Object.keys(idea.latest_session.answers).length / idea.latest_session.questions.length) * 100)}%"
                ></div>
              </div>
              <div class="flex space-x-2">
                <Button size="sm" href="/ideas/{idea.id}/refine">
                  {idea.latest_session.is_complete ? 'View Session' : 'Continue Session'}
                </Button>
                {#if idea.latest_session.is_complete && !idea.has_active_plan}
                  <Button size="sm" variant="outline" on:click={() => goto(`/ideas/${idea.id}/refine`)}>
                    Generate Plan
                  </Button>
                {/if}
              </div>
            </div>
          </div>
        {/if}

        <!-- Quick Stats -->
        <div class="bg-white rounded-lg shadow-sm border border-secondary-200">
          <div class="p-6">
            <h2 class="text-lg font-semibold text-secondary-900 mb-4">Progress Summary</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 class="text-sm font-medium text-secondary-700 mb-2">Refinement Progress</h3>
                <div class="text-2xl font-bold text-secondary-900">{idea.refinement_sessions_count}</div>
                <div class="text-sm text-secondary-600">
                  {idea.refinement_sessions_count === 0 ? 'No sessions yet' : 
                   idea.refinement_sessions_count === 1 ? '1 session completed' : 
                   `${idea.refinement_sessions_count} sessions completed`}
                </div>
              </div>
              <div>
                <h3 class="text-sm font-medium text-secondary-700 mb-2">Implementation Planning</h3>
                <div class="text-2xl font-bold text-secondary-900">{idea.plans_count}</div>
                <div class="text-sm text-secondary-600">
                  {idea.plans_count === 0 ? 'No plans yet' : 
                   idea.has_active_plan ? '1 active plan' : 
                   `${idea.plans_count} plans available`}
                </div>
              </div>
            </div>
          </div>
        </div>
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