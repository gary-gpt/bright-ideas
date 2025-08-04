<script lang="ts">
  /**
   * Idea refinement page with AI chat
   */
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { ideaActions, currentIdea } from '$stores/ideas';
  import { conversationActions, currentConversation } from '$stores/conversations';
  import { toastActions } from '$stores/ui';
  import IdeaRefinement from '$components/capture/IdeaRefinement.svelte';
  import LoadingSpinner from '$components/shared/LoadingSpinner.svelte';

  let ideaId: string;
  let loading = true;
  let messageLoading = false;

  $: ideaId = $page.params.id;

  onMount(async () => {
    if (!ideaId) {
      goto('/capture');
      return;
    }

    try {
      // Load the idea
      await ideaActions.loadIdea(ideaId);
      
      // Check if we have an existing refinement conversation
      const conversations = await conversationActions.loadConversations(ideaId, 'capture');
      
      if (conversations.length > 0) {
        // Use existing conversation
        await conversationActions.loadConversation(conversations[0].id);
      } else {
        // Start new refinement conversation
        await conversationActions.startRefinementConversation(ideaId);
      }
    } catch (error) {
      console.error('Failed to load refinement page:', error);
      toastActions.error('Failed to load idea. Please try again.');
      goto('/ideas');
    } finally {
      loading = false;
    }
  });

  async function handleSendMessage(event: CustomEvent<string>) {
    if (!$currentConversation) return;

    messageLoading = true;
    try {
      await conversationActions.sendMessage($currentConversation.id, event.detail);
    } catch (error) {
      console.error('Failed to send message:', error);
      toastActions.error('Failed to send message. Please try again.');
    } finally {
      messageLoading = false;
    }
  }

  async function handleUpdateIdea(event: CustomEvent<any>) {
    if (!$currentIdea) return;

    try {
      await ideaActions.updateIdea($currentIdea.id, event.detail);
      toastActions.success('Idea updated successfully!');
    } catch (error) {
      console.error('Failed to update idea:', error);
      toastActions.error('Failed to update idea. Please try again.');
    }
  }

  function handleFinishRefinement() {
    if ($currentIdea) {
      // Update idea status to refined
      ideaActions.updateIdea($currentIdea.id, { status: 'refined' });
      toastActions.success('Idea refinement completed!');
      goto(`/ideas/${$currentIdea.id}`);
    } else {
      goto('/ideas');
    }
  }
</script>

<svelte:head>
  <title>Refine Idea - Bright Ideas</title>
  <meta name="description" content="Refine your idea with AI-powered conversation" />
</svelte:head>

<div class="h-screen flex flex-col p-4">
  {#if loading}
    <div class="flex-1 flex items-center justify-center">
      <LoadingSpinner size="lg" message="Loading refinement session..." />
    </div>
  {:else if $currentConversation && $currentIdea}
    <div class="flex-1 min-h-0">
      <IdeaRefinement
        conversation={$currentConversation}
        {loading}
        {messageLoading}
        on:sendMessage={handleSendMessage}
        on:updateIdea={handleUpdateIdea}
        on:finishRefinement={handleFinishRefinement}
      />
    </div>
  {:else}
    <div class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <h2 class="text-xl font-semibold text-secondary-900 mb-2">
          Idea not found
        </h2>
        <p class="text-secondary-600 mb-4">
          The idea you're looking for doesn't exist or couldn't be loaded.
        </p>
        <a href="/ideas" class="text-primary-600 hover:text-primary-700">
          Browse all ideas →
        </a>
      </div>
    </div>
  {/if}
</div>