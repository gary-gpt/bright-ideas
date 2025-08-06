<script lang="ts">
  /**
   * Root layout component with global UI elements
   */
  import '../app.postcss';
  import { onMount } from 'svelte';
  import { toasts, toastActions, globalLoading } from '$lib/stores';
  import Navigation from '$lib/components/shared/Navigation.svelte';
  import Toast from '$lib/components/shared/Toast.svelte';
  import LoadingSpinner from '$lib/components/shared/LoadingSpinner.svelte';

  onMount(() => {
    // Initialize any global setup here
    console.log('Bright Ideas app initialized');
  });
</script>

<svelte:head>
  <title>Bright Ideas - AI-Powered Brainstorming</title>
  <meta name="description" content="Transform your vague ideas into actionable plans with AI assistance" />
</svelte:head>

<div class="min-h-screen bg-secondary-50">
  <Navigation>
    <main class="flex-1">
      <slot />
    </main>
  </Navigation>
</div>

  <!-- Global loading overlay -->
  {#if $globalLoading.isLoading}
    <div class="fixed inset-0 z-50 bg-white bg-opacity-75 flex items-center justify-center">
      <LoadingSpinner 
        size="lg" 
        message={$globalLoading.message || 'Loading...'} 
      />
    </div>
  {/if}

  <!-- Toast notifications -->
  {#if $toasts.length > 0}
    <div class="fixed top-4 right-4 z-40 space-y-2 max-w-md">
      {#each $toasts as toast (toast.id)}
        <Toast 
          {toast} 
          on:remove={(e) => toastActions.remove(e.detail)}
        />
      {/each}
    </div>
  {/if}