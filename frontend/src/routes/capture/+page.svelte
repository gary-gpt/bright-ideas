<script lang="ts">
  /**
   * Idea capture page - initial form
   */
  import { goto } from '$app/navigation';
  import { ideaActions } from '$lib/stores';
  import { toastActions } from '$lib/stores';
  import IdeaCapture from '$lib/components/capture/IdeaCapture.svelte';
  import type { IdeaCaptureForm } from '$lib/types';

  let loading = false;

  async function handleIdeaSubmit(event: CustomEvent<IdeaCaptureForm>) {
    const form = event.detail;
    loading = true;

    try {
      console.log('Submitting idea for refinement:', {
        title: form.title,
        original_description: form.description,
        tags: form.tags
      });
      
      const newIdea = await ideaActions.createIdea({
        title: form.title,
        original_description: form.description,
        tags: form.tags,
        is_unrefined: false
      });

      console.log('Idea created successfully:', newIdea);
      toastActions.success('Idea captured successfully! Starting AI refinement...');
      
      // Navigate to refinement page to continue with structured AI assistance
      goto(`/ideas/${newIdea.id}/refine`);
    } catch (error) {
      console.error('Failed to create idea - detailed error:', {
        error: error,
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : undefined
      });
      toastActions.error(`Failed to capture idea: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      loading = false;
    }
  }

  async function handleQuickSubmit(event: CustomEvent<IdeaCaptureForm>) {
    const form = event.detail;
    loading = true;

    try {
      console.log('Quick saving idea:', {
        title: form.title,
        original_description: form.description,
        tags: form.tags
      });
      
      const newIdea = await ideaActions.createIdea({
        title: form.title,
        original_description: form.description,
        tags: form.tags,
        is_unrefined: true
      });

      console.log('Idea quick saved successfully:', newIdea);
      toastActions.success('Idea saved! You can refine it later from your ideas list.');
      
      // Navigate to the ideas list
      goto('/ideas');
    } catch (error) {
      console.error('Failed to save idea - detailed error:', {
        error: error,
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : undefined
      });
      toastActions.error(`Failed to save idea: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>Capture Idea - Bright Ideas</title>
  <meta name="description" content="Capture and refine your next big idea with AI assistance" />
</svelte:head>

<div class="min-h-screen py-8 px-4">
  <IdeaCapture 
    {loading}
    on:submit={handleIdeaSubmit}
    on:quickSubmit={handleQuickSubmit}
  />
</div>