<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import Button from '$lib/components/shared/Button.svelte';
  import type { Plan } from '$lib/types';

  export let plans: Plan[] = [];
  export let loading: boolean = false;
  export let emptyMessage: string = 'No implementation plans yet';
  export let showCreateButton: boolean = true;

  const dispatch = createEventDispatcher<{
    select: { plan: Plan };
    activate: { plan: Plan };
    export: { plan: Plan; format: 'json' | 'markdown' };
    delete: { plan: Plan };
    create: void;
  }>();

  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString([], {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  }

  function getStatusColor(status: string): string {
    const colors = {
      draft: 'bg-gray-100 text-gray-800',
      generated: 'bg-blue-100 text-blue-800',
      edited: 'bg-yellow-100 text-yellow-800',
      published: 'bg-green-100 text-green-800'
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  }

  function handleSelect(plan: Plan) {
    dispatch('select', { plan });
  }

  function handleActivate(plan: Plan, event: Event) {
    event.stopPropagation();
    dispatch('activate', { plan });
  }

  function handleExport(plan: Plan, format: 'json' | 'markdown', event: Event) {
    event.stopPropagation();
    dispatch('export', { plan, format });
  }

  function handleDelete(plan: Plan, event: Event) {
    event.stopPropagation();
    if (confirm('Are you sure you want to delete this plan? This action cannot be undone.')) {
      dispatch('delete', { plan });
    }
  }

  function handleCreate() {
    dispatch('create');
  }

  $: activePlan = plans.find(plan => plan.is_active);
  $: sortedPlans = [...plans].sort((a, b) => {
    // Active plan first, then by creation date (newest first)
    if (a.is_active && !b.is_active) return -1;
    if (!a.is_active && b.is_active) return 1;
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });
</script>

<div class="space-y-4">
  <!-- Header -->
  <div class="flex items-center justify-between">
    <div>
      <h2 class="text-lg font-semibold text-secondary-900">Implementation Plans</h2>
      <p class="text-sm text-secondary-600">
        {plans.length === 0 ? emptyMessage : 
         plans.length === 1 ? '1 plan available' : 
         `${plans.length} plans available`}
        {#if activePlan}
          • 1 active
        {/if}
      </p>
    </div>
    {#if showCreateButton}
      <Button on:click={handleCreate} size="sm">
        Create New Plan
      </Button>
    {/if}
  </div>

  {#if loading}
    <!-- Loading State -->
    <div class="space-y-4">
      {#each Array(3) as _}
        <div class="bg-white rounded-lg border border-secondary-200 p-4">
          <div class="animate-pulse">
            <div class="flex items-center justify-between mb-3">
              <div class="h-4 bg-secondary-200 rounded w-32"></div>
              <div class="h-6 bg-secondary-200 rounded w-16"></div>
            </div>
            <div class="space-y-2">
              <div class="h-3 bg-secondary-200 rounded w-full"></div>
              <div class="h-3 bg-secondary-200 rounded w-3/4"></div>
            </div>
            <div class="flex items-center justify-between mt-4">
              <div class="h-3 bg-secondary-200 rounded w-24"></div>
              <div class="flex space-x-2">
                <div class="h-6 bg-secondary-200 rounded w-16"></div>
                <div class="h-6 bg-secondary-200 rounded w-16"></div>
              </div>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {:else if plans.length === 0}
    <!-- Empty State -->
    <div class="text-center py-12 bg-white rounded-lg border border-secondary-200">
      <div class="w-12 h-12 mx-auto mb-4 bg-secondary-100 rounded-full flex items-center justify-center">
        <svg class="w-6 h-6 text-secondary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
      </div>
      <h3 class="text-lg font-medium text-secondary-900 mb-2">No Plans Yet</h3>
      <p class="text-secondary-600 mb-4">{emptyMessage}</p>
      {#if showCreateButton}
        <Button on:click={handleCreate}>
          Create Your First Plan
        </Button>
      {/if}
    </div>
  {:else}
    <!-- Plans List -->
    <div class="space-y-3">
      {#each sortedPlans as plan}
        <div 
          class="bg-white rounded-lg border border-secondary-200 hover:border-secondary-300 transition-colors cursor-pointer"
          on:click={() => handleSelect(plan)}
          on:keydown={(e) => e.key === 'Enter' && handleSelect(plan)}
          role="button"
          tabindex="0"
        >
          <div class="p-4">
            <!-- Plan Header -->
            <div class="flex items-start justify-between mb-3">
              <div class="flex items-center space-x-2">
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium {getStatusColor(plan.status)}">
                  {plan.status}
                </span>
                {#if plan.is_active}
                  <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Active Plan
                  </span>
                {/if}
              </div>
              <div class="text-xs text-secondary-500">
                {formatDate(plan.created_at)}
              </div>
            </div>

            <!-- Plan Summary -->
            <div class="mb-3">
              <p class="text-sm text-secondary-700 line-clamp-2">
                {plan.summary}
              </p>
            </div>

            <!-- Plan Stats -->
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-4 text-xs text-secondary-500">
                <span>{plan.steps.length} steps</span>
                <span>•</span>
                <span>{plan.resources.length} resources</span>
                {#if plan.updated_at !== plan.created_at}
                  <span>•</span>
                  <span>Updated {formatDate(plan.updated_at)}</span>
                {/if}
              </div>

              <!-- Action Buttons -->
              <div class="flex items-center space-x-1">
                {#if !plan.is_active}
                  <Button 
                    size="sm" 
                    variant="outline"
                    on:click={(e) => handleActivate(plan, e)}
                  >
                    Activate
                  </Button>
                {/if}
                
                <Button 
                  size="sm" 
                  variant="ghost"
                  on:click={(e) => handleExport(plan, 'markdown', e)}
                  title="Export as Markdown"
                >
                  MD
                </Button>
                
                <Button 
                  size="sm" 
                  variant="ghost"
                  on:click={(e) => handleExport(plan, 'json', e)}
                  title="Export as JSON"
                >
                  JSON
                </Button>
                
                <Button 
                  size="sm" 
                  variant="ghost"
                  on:click={(e) => handleDelete(plan, e)}
                  title="Delete plan"
                  class="text-red-600 hover:text-red-800"
                >
                  ×
                </Button>
              </div>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>