<script lang="ts">
  export let current: number;
  export let total: number;
  export let label: string = 'Progress';
  export let size: 'sm' | 'md' | 'lg' = 'md';
  export let showPercentage: boolean = true;
  export let showFraction: boolean = true;
  export let color: 'primary' | 'green' | 'blue' | 'yellow' = 'primary';

  $: percentage = total > 0 ? Math.round((current / total) * 100) : 0;
  
  $: sizeClasses = {
    sm: 'h-1',
    md: 'h-2', 
    lg: 'h-3'
  };

  $: colorClasses = {
    primary: 'bg-primary-600',
    green: 'bg-green-600',
    blue: 'bg-blue-600',
    yellow: 'bg-yellow-600'
  };

  $: textColorClasses = {
    primary: 'text-primary-600',
    green: 'text-green-600', 
    blue: 'text-blue-600',
    yellow: 'text-yellow-600'
  };
</script>

<div class="w-full">
  <!-- Progress Header -->
  <div class="flex items-center justify-between mb-2">
    <span class="text-sm font-medium text-secondary-700">{label}</span>
    <div class="flex items-center space-x-2 text-sm text-secondary-600">
      {#if showFraction}
        <span>{current} of {total}</span>
      {/if}
      {#if showPercentage}
        <span class="font-medium {textColorClasses[color]}">{percentage}%</span>
      {/if}
    </div>
  </div>

  <!-- Progress Bar -->
  <div class="w-full bg-secondary-200 rounded-full {sizeClasses[size]}">
    <div 
      class="{sizeClasses[size]} rounded-full transition-all duration-500 ease-out {colorClasses[color]}" 
      style="width: {percentage}%"
    ></div>
  </div>

  <!-- Optional Status Text -->
  {#if $$slots.default}
    <div class="mt-1 text-xs text-secondary-500">
      <slot />
    </div>
  {/if}
</div>