<script lang="ts">
  /**
   * Reusable modal component with backdrop and animations
   */
  import { createEventDispatcher } from 'svelte';
  import { fade, scale } from 'svelte/transition';
  import { X } from 'lucide-svelte';
  import Button from './Button.svelte';

  export let isOpen = false;
  export let title = '';
  export let size: 'sm' | 'md' | 'lg' | 'xl' = 'md';
  export let closeable = true;
  export let closeOnBackdrop = true;

  const dispatch = createEventDispatcher<{ close: void }>();

  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl'
  };

  function handleClose() {
    if (closeable) {
      dispatch('close');
    }
  }

  function handleBackdropClick(event: MouseEvent) {
    if (closeOnBackdrop && event.target === event.currentTarget) {
      handleClose();
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape' && closeable) {
      handleClose();
    }
  }
</script>

{#if isOpen}
  <div
    class="fixed inset-0 z-50 overflow-y-auto"
    role="dialog"
    aria-modal="true"
    aria-labelledby={title ? 'modal-title' : undefined}
    on:keydown={handleKeydown}
  >
    <!-- Backdrop -->
    <div
      class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
      transition:fade={{ duration: 200 }}
      on:click={handleBackdropClick}
    />

    <!-- Modal container -->
    <div class="flex min-h-full items-center justify-center p-4">
      <div
        class="relative w-full {sizeClasses[size]} bg-white rounded-lg shadow-xl"
        transition:scale={{ duration: 200, start: 0.95 }}
      >
        <!-- Header -->
        {#if title || closeable}
          <div class="flex items-center justify-between p-6 pb-4">
            {#if title}
              <h2 id="modal-title" class="text-lg font-semibold text-secondary-900">
                {title}
              </h2>
            {/if}
            {#if closeable}
              <button
                type="button"
                class="rounded-md text-secondary-400 hover:text-secondary-600 focus:outline-none focus:ring-2 focus:ring-primary-500"
                on:click={handleClose}
              >
                <X size={20} />
              </button>
            {/if}
          </div>
        {/if}

        <!-- Content -->
        <div class="px-6 {title || closeable ? '' : 'pt-6'}">
          <slot />
        </div>

        <!-- Footer -->
        {#if $$slots.footer}
          <div class="flex justify-end space-x-3 p-6 pt-4 bg-secondary-50 rounded-b-lg">
            <slot name="footer" />
          </div>
        {/if}
      </div>
    </div>
  </div>
{/if}