<script lang="ts">
  /**
   * Toast notification component
   */
  import { createEventDispatcher } from 'svelte';
  import { fly } from 'svelte/transition';
  import { CheckCircle, AlertCircle, AlertTriangle, Info, X } from 'lucide-svelte';
  import type { Toast } from '$lib/types';

  export let toast: Toast;

  const dispatch = createEventDispatcher<{ remove: string }>();

  const icons = {
    success: CheckCircle,
    error: AlertCircle,
    warning: AlertTriangle,
    info: Info
  };

  const colorClasses = {
    success: 'bg-green-50 border-green-200 text-green-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800'
  };

  const iconColorClasses = {
    success: 'text-green-400',
    error: 'text-red-400',
    warning: 'text-yellow-400',
    info: 'text-blue-400'
  };

  function handleRemove() {
    dispatch('remove', toast.id);
  }
</script>

<div
  class="w-full bg-white shadow-lg rounded-lg pointer-events-auto border {colorClasses[toast.type]}"
  transition:fly={{ x: 400, duration: 300 }}
>
  <div class="p-4">
    <div class="flex items-start">
      <div class="flex-shrink-0 {iconColorClasses[toast.type]}">
        <svelte:component this={icons[toast.type]} size={20} />
      </div>
      <div class="ml-3 flex-1 min-w-0">
        <p class="text-sm font-medium break-words">
          {toast.message}
        </p>
      </div>
      <div class="ml-4 flex-shrink-0 flex">
        <button
          type="button"
          class="rounded-md inline-flex text-secondary-400 hover:text-secondary-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          on:click={handleRemove}
        >
          <X size={16} />
        </button>
      </div>
    </div>
  </div>
</div>