<script lang="ts">
  /**
   * Idea capture page - initial form
   */
  import { goto } from '$app/navigation';
  import { ideaActions } from '$lib/stores/ideas';
  import { toastActions } from '$lib/stores/ui';
  import IdeaCapture from '$lib/components/capture/IdeaCapture.svelte';
  import type { IdeaCaptureForm } from '$lib/types';

  let loading = false;

  async function handleIdeaSubmit(event: CustomEvent<IdeaCaptureForm>) {
    const form = event.detail;
    loading = true;

    try {
      const newIdea = await ideaActions.createIdea({
        title: form.title,
        original_description: form.description,
        tags: form.tags
      });

      toastActions.success('Idea captured successfully!');
      
      // Navigate to refinement page
      goto(`/capture/refine/${newIdea.id}`);
    } catch (error) {
      console.error('Failed to create idea:', error);
      toastActions.error('Failed to capture idea. Please try again.');
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
  />
</div>