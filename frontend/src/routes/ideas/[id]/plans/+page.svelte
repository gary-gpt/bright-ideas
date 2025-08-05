<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { 
    ideaActions, 
    planActions, 
    refinementActions,
    currentIdea,
    ideaPlans,
    refinementSessions
  } from '$lib/stores';
  import { toastActions } from '$lib/stores';
  import Button from '$lib/components/shared/Button.svelte';
  import LoadingSpinner from '$lib/components/shared/LoadingSpinner.svelte';
  import PlanList from '$lib/components/plans/PlanList.svelte';
  import type { IdeaDetail, Plan, RefinementSession } from '$lib/types';

  let idea: IdeaDetail | null = null;
  let plans: Plan[] = [];
  let sessions: RefinementSession[] = [];
  let loading = true;
  let actionLoading = false;

  $: ideaId = $page.params.id;
  $: completedSessions = sessions.filter(s => s.is_complete);
  $: canCreatePlan = completedSessions.length > 0;

  onMount(async () => {
    if (ideaId) {
      try {
        // Load idea, plans, and sessions in parallel
        const [loadedIdea, loadedPlans, loadedSessions] = await Promise.all([
          ideaActions.loadIdea(ideaId),
          planActions.loadIdeaPlans(ideaId),
          refinementActions.loadIdeaSessions(ideaId).catch(() => [])
        ]);
        
        idea = loadedIdea;
        plans = loadedPlans;
        sessions = loadedSessions;
      } catch (error) {
        console.error('Failed to load plans data:', error);
        toastActions.error('Failed to load implementation plans');
        goto(`/ideas/${ideaId}`);
      } finally {
        loading = false;
      }
    }
  });

  async function handleSelectPlan(event: CustomEvent<{ plan: Plan }>) {
    const { plan } = event.detail;
    goto(`/ideas/${ideaId}/plans/${plan.id}`);
  }

  async function handleActivatePlan(event: CustomEvent<{ plan: Plan }>) {
    const { plan } = event.detail;
    
    actionLoading = true;
    try {
      await planActions.activatePlan(plan.id);
      
      // Update local plans array
      plans = plans.map(p => ({
        ...p,
        is_active: p.id === plan.id
      }));
      
      toastActions.success('Plan activated successfully!');
    } catch (error) {
      console.error('Failed to activate plan:', error);
      toastActions.error('Failed to activate plan');
    } finally {
      actionLoading = false;
    }
  }

  async function handleExportPlan(event: CustomEvent<{ plan: Plan; format: 'json' | 'markdown' }>) {
    const { plan, format } = event.detail;
    
    try {
      if (format === 'json') {
        await planActions.exportPlanJson(plan.id, `${idea?.title}_plan.json`);
      } else {
        await planActions.exportPlanMarkdown(plan.id, `${idea?.title}_plan.md`);
      }
      toastActions.success(`Plan exported as ${format.toUpperCase()}`);
    } catch (error) {
      console.error('Failed to export plan:', error);
      toastActions.error('Failed to export plan');
    }
  }

  async function handleDeletePlan(event: CustomEvent<{ plan: Plan }>) {
    const { plan } = event.detail;
    
    actionLoading = true;
    try {
      await planActions.deletePlan(plan.id);
      
      // Remove from local plans array
      plans = plans.filter(p => p.id !== plan.id);
      
      toastActions.success('Plan deleted successfully');
    } catch (error) {
      console.error('Failed to delete plan:', error);
      toastActions.error('Failed to delete plan');
    } finally {
      actionLoading = false;
    }
  }

  function handleCreatePlan() {
    if (completedSessions.length === 0) {
      toastActions.error('Complete a refinement session first to generate a plan');
      goto(`/ideas/${ideaId}/refine`);
      return;
    }
    
    // For now, use the most recent completed session
    const latestSession = completedSessions[0];
    goto(`/ideas/${ideaId}/refine?generate=${latestSession.id}`);
  }

  function startRefinement() {
    goto(`/ideas/${ideaId}/refine`);
  }
</script>

<svelte:head>
  <title>Plans: {idea ? idea.title : 'Loading...'} - Bright Ideas</title>
</svelte:head>

<div class="min-h-screen bg-secondary-50">
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="mb-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <Button variant="ghost" href="/ideas/{ideaId}" size="sm">
            ← Back to Idea
          </Button>
          <div>
            <h1 class="text-2xl font-bold text-secondary-900">
              Implementation Plans
            </h1>
            {#if idea}
              <p class="text-secondary-600">{idea.title}</p>
            {/if}
          </div>
        </div>
      </div>
    </div>

    {#if loading}
      <div class="flex justify-center py-12">
        <LoadingSpinner size="lg" message="Loading implementation plans..." />
      </div>
    {:else if idea}
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Main Content -->
        <div class="lg:col-span-2">
          <PlanList 
            {plans}
            loading={actionLoading}
            emptyMessage="No implementation plans created yet. Complete a refinement session to generate your first plan."
            showCreateButton={canCreatePlan}
            on:select={handleSelectPlan}
            on:activate={handleActivatePlan}
            on:export={handleExportPlan}
            on:delete={handleDeletePlan}
            on:create={handleCreatePlan}
          />
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
          <!-- Idea Summary -->
          <div class="bg-white rounded-lg shadow-sm border border-secondary-200 p-4">
            <h3 class="text-lg font-semibold text-secondary-900 mb-3">Idea Overview</h3>
            <div class="space-y-3">
              <div>
                <span class="text-sm font-medium text-secondary-700">Status:</span>
                <span class="ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {idea.status}
                </span>
              </div>
              <div>
                <span class="text-sm font-medium text-secondary-700">Progress:</span>
                <div class="mt-1 text-sm text-secondary-600">
                  <div>{idea.refinement_sessions_count} refinement sessions</div>
                  <div>{idea.plans_count} implementation plans</div>
                  <div class="text-{idea.has_active_plan ? 'green' : 'gray'}-600">
                    {idea.has_active_plan ? '✓ Active plan selected' : '○ No active plan'}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Refinement Sessions -->
          <div class="bg-white rounded-lg shadow-sm border border-secondary-200 p-4">
            <h3 class="text-lg font-semibold text-secondary-900 mb-3">Refinement Sessions</h3>
            {#if sessions.length === 0}
              <div class="text-center py-4">
                <p class="text-sm text-secondary-600 mb-3">No refinement sessions yet</p>
                <Button size="sm" on:click={startRefinement}>
                  Start Refinement
                </Button>
              </div>
            {:else}
              <div class="space-y-2">
                {#each sessions.slice(0, 3) as session}
                  <div class="flex items-center justify-between p-2 bg-secondary-50 rounded">
                    <div class="text-sm">
                      <div class="text-secondary-900">
                        {Object.keys(session.answers).length} of {session.questions.length} answered
                      </div>
                      <div class="text-xs text-secondary-500">
                        {new Date(session.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <span class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium {session.is_complete ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}">
                      {session.is_complete ? 'Complete' : 'In Progress'}
                    </span>
                  </div>
                {/each}
                {#if sessions.length > 3}
                  <div class="text-xs text-secondary-500 text-center pt-2">
                    +{sessions.length - 3} more sessions
                  </div>
                {/if}
              </div>
              
              <div class="mt-4 space-y-2">
                <Button size="sm" variant="outline" on:click={startRefinement} class="w-full">
                  Start New Session
                </Button>
                {#if completedSessions.length > 0}
                  <Button size="sm" on:click={handleCreatePlan} class="w-full">
                    Generate New Plan
                  </Button>
                {/if}
              </div>
            {/if}
          </div>

          <!-- Quick Actions -->
          <div class="bg-white rounded-lg shadow-sm border border-secondary-200 p-4">
            <h3 class="text-lg font-semibold text-secondary-900 mb-3">Quick Actions</h3>
            <div class="space-y-2">
              <Button 
                size="sm" 
                variant="outline" 
                href="/ideas/{ideaId}/refine"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Refine Idea
              </Button>
              
              <Button 
                size="sm" 
                variant="outline" 
                href="/ideas/{ideaId}"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                </svg>
                View Idea Details
              </Button>
              
              <Button 
                size="sm" 
                variant="outline" 
                href="/ideas"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                </svg>
                All Ideas
              </Button>
            </div>
          </div>
        </div>
      </div>
    {:else}
      <div class="text-center py-12">
        <h2 class="text-xl font-bold text-secondary-900 mb-2">Idea Not Found</h2>
        <p class="text-secondary-600 mb-4">The idea you're looking for doesn't exist or has been deleted.</p>
        <Button href="/ideas">Back to Ideas</Button>
      </div>
    {/if}
  </div>
</div>