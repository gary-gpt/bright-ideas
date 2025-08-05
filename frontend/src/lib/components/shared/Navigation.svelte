<script lang="ts">
  /**
   * Main navigation component with responsive design
   */
  import { page } from '$app/stores';
  import { sidebarOpen, isMobile, navigationActions } from '$lib/stores/ui';
  import { Lightbulb, Home, BookOpen, Settings, Menu, X, Archive } from 'lucide-svelte';
  import Button from './Button.svelte';

  const navItems = [
    { href: '/', icon: Home, label: 'Dashboard' },
    { href: '/capture', icon: Lightbulb, label: 'Capture' },
    { href: '/ideas', icon: BookOpen, label: 'Ideas' },
    { href: '/ideas/archive', icon: Archive, label: 'Archive' },
    { href: '/settings', icon: Settings, label: 'Settings' }
  ];

  $: currentPath = $page.url.pathname;

  function isActiveRoute(href: string): boolean {
    if (href === '/') {
      return currentPath === '/';
    }
    return currentPath.startsWith(href);
  }
</script>

<!-- Mobile menu button -->
{#if $isMobile}
  <div class="fixed top-4 left-4 z-40 lg:hidden">
    <Button
      variant="ghost"
      size="sm"
      on:click={navigationActions.toggleSidebar}
    >
      {#if $sidebarOpen}
        <X size={20} />
      {:else}
        <Menu size={20} />
      {/if}
    </Button>
  </div>
{/if}

<!-- Sidebar backdrop (mobile) -->
{#if $sidebarOpen && $isMobile}
  <div
    class="fixed inset-0 z-20 bg-black bg-opacity-50 lg:hidden"
    on:click={navigationActions.closeSidebar}
  />
{/if}

<!-- Sidebar -->
<nav
  class="fixed left-0 top-0 z-30 h-full w-64 transform bg-white shadow-lg transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:shadow-none
    {$sidebarOpen ? 'translate-x-0' : '-translate-x-full'}"
>
  <!-- Header -->
  <div class="flex h-16 items-center justify-center border-b border-secondary-200 bg-primary-600">
    <div class="flex items-center space-x-2 text-white">
      <Lightbulb size={24} />
      <span class="text-lg font-bold">Bright Ideas</span>
    </div>
  </div>

  <!-- Navigation items -->
  <div class="flex flex-col space-y-1 p-4 pb-20">
    {#each navItems as item}
      <a
        href={item.href}
        class="flex items-center space-x-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors
          {isActiveRoute(item.href)
            ? 'bg-primary-100 text-primary-700'
            : 'text-secondary-600 hover:bg-secondary-100 hover:text-secondary-900'}"
        on:click={() => $isMobile && navigationActions.closeSidebar()}
      >
        <svelte:component this={item.icon} size={18} />
        <span>{item.label}</span>
      </a>
    {/each}
  </div>

  <!-- Footer -->
  <div class="absolute bottom-4 left-4 right-4">
    <div class="rounded-lg bg-secondary-50 p-3">
      <p class="text-xs text-secondary-600">
        AI-powered brainstorming and planning
      </p>
    </div>
  </div>
</nav>

<!-- Main content area adjustment -->
<div class="lg:ml-64">
  <slot />
</div>