<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { ideaActions, planActions } from '$lib/stores';
  import { toastActions } from '$lib/stores';
  import Button from '$lib/components/shared/Button.svelte';
  import LoadingSpinner from '$lib/components/shared/LoadingSpinner.svelte';
  import PlanViewer from '$lib/components/plans/PlanViewer.svelte';
  import type { IdeaDetail, Plan } from '$lib/types';

  let idea: IdeaDetail | null = null;
  let plan: Plan | null = null;
  let loading = true;
  let actionLoading = false;

  $: ideaId = $page.params.id;
  $: planId = $page.params.planId;

  onMount(async () => {
    if (ideaId && planId) {
      try {
        // Load idea and plan in parallel
        const [loadedIdea, loadedPlan] = await Promise.all([
          ideaActions.loadIdea(ideaId),
          planActions.loadPlan(planId)
        ]);
        
        idea = loadedIdea;
        plan = loadedPlan;
        
        // Verify the plan belongs to this idea
        if (plan.idea_id !== ideaId) {
          throw new Error('Plan does not belong to this idea');
        }
      } catch (error) {
        console.error('Failed to load plan:', error);
        toastActions.error('Failed to load implementation plan');
        goto(`/ideas/${ideaId}/plans`);
      } finally {
        loading = false;
      }
    }
  });

  async function handleExport(event: CustomEvent<{ format: 'json' | 'markdown' }>) {
    if (!plan || !idea) return;
    
    const { format } = event.detail;
    
    try {
      if (format === 'json') {
        await planActions.exportPlanJson(plan.id, `${idea.title}_plan.json`);
      } else {
        await planActions.exportPlanMarkdown(plan.id, `${idea.title}_plan.md`);
      }
      toastActions.success(`Plan exported as ${format.toUpperCase()}`);
    } catch (error) {
      console.error('Failed to export plan:', error);
      toastActions.error('Failed to export plan');
    }
  }

  async function handleActivate() {
    if (!plan) return;
    
    actionLoading = true;
    try {
      const activatedPlan = await planActions.activatePlan(plan.id);
      plan = activatedPlan;
      toastActions.success('Plan activated successfully!');
    } catch (error) {
      console.error('Failed to activate plan:', error);
      toastActions.error('Failed to activate plan');
    } finally {
      actionLoading = false;
    }
  }

  function handleEdit() {
    // For now, redirect to plans list with edit mode
    // In a full implementation, this would open an edit modal or page
    toastActions.info('Plan editing will be available in a future update');
  }

  async function handleDelete() {
    if (!plan) return;
    
    if (confirm('Are you sure you want to delete this implementation plan? This action cannot be undone.')) {
      actionLoading = true;
      try {
        await planActions.deletePlan(plan.id);
        toastActions.success('Plan deleted successfully');
        goto(`/ideas/${ideaId}/plans`);
      } catch (error) {
        console.error('Failed to delete plan:', error);
        toastActions.error('Failed to delete plan');
      } finally {
        actionLoading = false;
      }
    }
  }

  function goToPlansList() {
    goto(`/ideas/${ideaId}/plans`);
  }

  function goToIdea() {
    goto(`/ideas/${ideaId}`);
  }

  function generateNewPlan() {
    goto(`/ideas/${ideaId}/refine`);
  }
</script>

<svelte:head>
  <title>Plan: {idea ? idea.title : 'Loading...'} - Bright Ideas</title>
</svelte:head>

<div class="min-h-screen bg-secondary-50">
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Breadcrumb Navigation -->
    <div class="mb-6">
      <nav class="flex items-center space-x-2 text-sm text-secondary-600">
        <button on:click={goToIdea} class="hover:text-secondary-900">
          {idea ? idea.title : 'Idea'}
        </button>
        <span>›</span>
        <button on:click={goToPlansList} class="hover:text-secondary-900">
          Plans
        </button>
        <span>›</span>
        <span class="text-secondary-900">Implementation Plan</span>
      </nav>
    </div>

    {#if loading}
      <div class="flex justify-center py-12">
        <LoadingSpinner size="lg" message="Loading implementation plan..." />
      </div>
    {:else if idea && plan}
      <!-- Plan Header -->
      <div class="mb-6">
        <div class="flex items-start justify-between">
          <div>
            <h1 class="text-2xl font-bold text-secondary-900 mb-2">
              Implementation Plan
            </h1>
            <p class="text-secondary-600">{idea.title}</p>
          </div>
          
          <!-- Header Actions -->
          <div class="flex space-x-2">
            <Button 
              size="sm" 
              variant="outline" 
              on:click={generateNewPlan}
            >
              Generate New Plan
            </Button>
            <Button 
              size="sm" 
              variant="ghost" 
              on:click={goToPlansList}
            >
              ← All Plans
            </Button>
          </div>
        </div>
      </div>

      <!-- Plan Content -->
      <div class="mb-6">
        <PlanViewer 
          {plan}
          showExportButtons={true}
          showActivateButton={!plan.is_active}
          on:export={handleExport}
          on:activate={handleActivate}
          on:edit={handleEdit}
          on:delete={handleDelete}
        />
      </div>

      <!-- Action Bar -->
      <div class="bg-white rounded-lg shadow-sm border border-secondary-200 p-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <div class="text-sm text-secondary-600">
              Created {new Date(plan.created_at).toLocaleDateString()}
              {#if plan.updated_at !== plan.created_at}
                • Updated {new Date(plan.updated_at).toLocaleDateString()}
              {/if}
            </div>
            {#if plan.is_active}
              <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Active Plan
              </span>
            {/if}
          </div>
          
          <div class="flex space-x-2">
            {#if !plan.is_active}
              <Button 
                size="sm"
                on:click={handleActivate}
                disabled={actionLoading}
                loading={actionLoading}
              >
                Make Active Plan
              </Button>
            {/if}
            
            <Button 
              size="sm" 
              variant="outline"
              on:click={() => handleExport(new CustomEvent('export', { detail: { format: 'markdown' } }))}
            >
              Export Markdown
            </Button>
            
            <Button 
              size="sm" 
              variant="outline"
              on:click={() => handleExport(new CustomEvent('export', { detail: { format: 'json' } }))}
            >
              Export JSON
            </Button>
            
            <Button 
              size="sm" 
              variant="ghost"
              on:click={handleDelete}
              disabled={actionLoading}
            >
              Delete Plan
            </Button>
          </div>
        </div>
      </div>

      <!-- Related Actions -->
      <div class="mt-6 bg-secondary-100 rounded-lg p-4">
        <h3 class="text-sm font-medium text-secondary-900 mb-3">Next Steps</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
          <Button 
            size="sm" 
            variant="outline"
            on:click={generateNewPlan}
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            Create New Plan
          </Button>
          
          <Button 
            size="sm" 
            variant="outline"
            href="/ideas/{ideaId}/refine"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            Refine Further
          </Button>
          
          <Button 
            size="sm" 
            variant="outline"
            href="/capture"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
            </svg>
            New Idea
          </Button>
        </div>
      </div>
    {:else}
      <div class="text-center py-12">
        <h2 class="text-xl font-bold text-secondary-900 mb-2">Plan Not Found</h2>
        <p class="text-secondary-600 mb-4">The implementation plan you're looking for doesn't exist or has been deleted.</p>
        <div class="flex justify-center space-x-3">
          <Button on:click={goToPlansList}>View All Plans</Button>
          <Button variant="outline" on:click={goToIdea}>Back to Idea</Button>
        </div>
      </div>
    {/if}
  </div>
</div>