<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import Button from '$lib/components/shared/Button.svelte';
  import type { Plan } from '$lib/types';

  export let plan: Plan;
  export let showExportButtons: boolean = true;
  export let showActivateButton: boolean = true;
  export let compact: boolean = false;

  const dispatch = createEventDispatcher<{
    export: { format: 'json' | 'markdown' };
    activate: void;
    edit: void;
    delete: void;
  }>();

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
      draft: 'bg-gray-100 text-gray-800 border-gray-200',
      generated: 'bg-blue-100 text-blue-800 border-blue-200',
      edited: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      published: 'bg-green-100 text-green-800 border-green-200'
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800 border-gray-200';
  }

  function handleExport(format: 'json' | 'markdown') {
    dispatch('export', { format });
  }

  function handleActivate() {
    dispatch('activate');
  }

  function handleEdit() {
    dispatch('edit');
  }

  function handleDelete() {
    dispatch('delete');
  }
</script>

<div class="bg-white rounded-lg shadow-sm border border-secondary-200 {compact ? 'p-4' : 'p-6'}">
  <!-- Plan Header -->
  <div class="flex items-start justify-between mb-4">
    <div class="flex-1">
      <div class="flex items-center space-x-3 mb-2">
        <h3 class="{compact ? 'text-lg' : 'text-xl'} font-semibold text-secondary-900">
          Implementation Plan
        </h3>
        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border {getStatusColor(plan.status)}">
          {plan.status}
        </span>
        {#if plan.is_active}
          <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 border-green-200">
            Active
          </span>
        {/if}
      </div>
      <div class="text-sm text-secondary-500 space-x-4">
        <span>Created {formatDate(plan.created_at)}</span>
        {#if plan.updated_at !== plan.created_at}
          <span>• Updated {formatDate(plan.updated_at)}</span>
        {/if}
      </div>
    </div>
    
    <!-- Action Buttons -->
    {#if !compact}
      <div class="flex space-x-2">
        {#if showActivateButton && !plan.is_active}
          <Button size="sm" variant="outline" on:click={handleActivate}>
            Make Active
          </Button>
        {/if}
        
        {#if showExportButtons}
          <Button size="sm" variant="outline" on:click={() => handleExport('markdown')}>
            Export MD
          </Button>
          <Button size="sm" variant="outline" on:click={() => handleExport('json')}>
            Export JSON
          </Button>
        {/if}
        
        <Button size="sm" variant="ghost" on:click={handleEdit}>
          Edit
        </Button>
      </div>
    {/if}
  </div>

  <!-- Plan Summary -->
  <div class="mb-6">
    <h4 class="text-sm font-medium text-secondary-700 mb-2">Summary</h4>
    <div class="prose prose-sm max-w-none text-secondary-700">
      <p class="whitespace-pre-wrap">{plan.summary}</p>
    </div>
  </div>

  <!-- Plan Steps -->
  <div class="mb-6">
    <h4 class="text-sm font-medium text-secondary-700 mb-3">
      Implementation Steps ({plan.steps.length})
    </h4>
    <div class="space-y-3">
      {#each plan.steps as step}
        <div class="flex items-start space-x-3 p-3 bg-secondary-50 rounded-lg">
          <div class="flex-shrink-0 w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center">
            <span class="text-xs font-medium text-primary-600">{step.order}</span>
          </div>
          <div class="flex-1 min-w-0">
            <h5 class="text-sm font-medium text-secondary-900 mb-1">{step.title}</h5>
            <p class="text-sm text-secondary-600 mb-2">{step.description}</p>
            {#if step.estimated_time}
              <div class="flex items-center space-x-2">
                <svg class="w-3 h-3 text-secondary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span class="text-xs text-secondary-500">{step.estimated_time}</span>
              </div>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  </div>

  <!-- Plan Resources -->
  {#if plan.resources.length > 0}
    <div class="mb-4">
      <h4 class="text-sm font-medium text-secondary-700 mb-3">
        Helpful Resources ({plan.resources.length})
      </h4>
      <div class="grid grid-cols-1 {compact ? 'gap-2' : 'gap-3'}">
        {#each plan.resources as resource}
          <div class="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
            <div class="flex-shrink-0">
              <div class="w-2 h-2 bg-blue-400 rounded-full mt-2"></div>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center space-x-2 mb-1">
                <span class="text-sm font-medium text-blue-900">{resource.title}</span>
                <span class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-700">
                  {resource.type}
                </span>
              </div>
              {#if resource.description}
                <p class="text-sm text-blue-700 mb-2">{resource.description}</p>
              {/if}
              {#if resource.url}
                <a 
                  href={resource.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  class="inline-flex items-center text-xs text-blue-600 hover:text-blue-800 hover:underline"
                >
                  Visit Resource
                  <svg class="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                  </svg>
                </a>
              {/if}
            </div>
          </div>
        {/each}
      </div>
    </div>
  {/if}

  <!-- Compact Actions -->
  {#if compact && (showExportButtons || showActivateButton)}
    <div class="flex items-center justify-between pt-4 border-t border-secondary-200">
      <div class="text-xs text-secondary-500">
        {plan.steps.length} steps • {plan.resources.length} resources
      </div>
      <div class="flex space-x-2">
        {#if showActivateButton && !plan.is_active}
          <Button size="sm" variant="outline" on:click={handleActivate}>
            Activate
          </Button>
        {/if}
        {#if showExportButtons}
          <Button size="sm" variant="ghost" on:click={() => handleExport('markdown')}>
            Export
          </Button>
        {/if}
      </div>
    </div>
  {/if}
</div>