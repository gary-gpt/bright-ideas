<script lang="ts">
  /**
   * Initial idea capture form component
   */
  import { createEventDispatcher } from 'svelte';
  import { Lightbulb, ArrowRight } from 'lucide-svelte';
  import Button from '$lib/components/shared/Button.svelte';
  import type { IdeaCaptureForm } from '$lib/types';

  export let loading = false;

  const dispatch = createEventDispatcher<{ 
    submit: IdeaCaptureForm;
    quickSubmit: IdeaCaptureForm;
  }>();

  let form: IdeaCaptureForm = {
    title: '',
    description: '',
    tags: []
  };

  let tagInput = '';

  function handleSubmit() {
    if (form.title.trim() && form.description.trim()) {
      dispatch('submit', form);
    }
  }

  function handleQuickSubmit() {
    if (form.title.trim() && form.description.trim()) {
      dispatch('quickSubmit', form);
    }
  }

  function addTag() {
    const tag = tagInput.trim().toLowerCase();
    if (tag && !form.tags.includes(tag)) {
      form.tags = [...form.tags, tag];
      tagInput = '';
    }
  }

  function removeTag(tagToRemove: string) {
    form.tags = form.tags.filter(tag => tag !== tagToRemove);
  }

  function handleTagKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      event.preventDefault();
      addTag();
    }
  }

  $: isValid = form.title.trim().length > 0 && form.description.trim().length >= 10;
</script>

<div class="max-w-2xl mx-auto">
  <div class="bg-white rounded-lg shadow-sm border border-secondary-200 p-6">
    <!-- Header -->
    <div class="flex items-center space-x-3 mb-6">
      <div class="flex-shrink-0 p-2 bg-primary-100 rounded-lg">
        <Lightbulb size={24} class="text-primary-600" />
      </div>
      <div>
        <h2 class="text-xl font-semibold text-secondary-900">Capture Your Idea</h2>
        <p class="text-sm text-secondary-600">
          Start with a rough concept - we'll help you refine it
        </p>
      </div>
    </div>

    <form on:submit|preventDefault={handleSubmit} class="space-y-6">
      <!-- Title -->
      <div>
        <label for="title" class="block text-sm font-medium text-secondary-700 mb-2">
          Idea Title
        </label>
        <input
          id="title"
          type="text"
          bind:value={form.title}
          placeholder="Give your idea a catchy name..."
          class="w-full px-3 py-2 border border-secondary-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
          maxlength="200"
          required
        />
        <p class="mt-1 text-xs text-secondary-500">
          {form.title.length}/200 characters
        </p>
      </div>

      <!-- Description -->
      <div>
        <label for="description" class="block text-sm font-medium text-secondary-700 mb-2">
          Describe Your Idea
        </label>
        <textarea
          id="description"
          bind:value={form.description}
          placeholder="Tell us about your idea... What problem does it solve? Who would use it? Don't worry about being perfect - just get your thoughts down!"
          rows="6"
          class="w-full px-3 py-2 border border-secondary-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 resize-none"
          required
        />
        <p class="mt-1 text-xs text-secondary-500">
          Minimum 10 characters ({form.description.length} characters)
        </p>
      </div>

      <!-- Tags -->
      <div>
        <label for="tags" class="block text-sm font-medium text-secondary-700 mb-2">
          Tags (Optional)
        </label>
        <div class="flex flex-wrap gap-2 mb-2">
          {#each form.tags as tag}
            <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
              {tag}
              <button
                type="button"
                class="ml-1 text-primary-600 hover:text-primary-800"
                on:click={() => removeTag(tag)}
              >
                ×
              </button>
            </span>
          {/each}
        </div>
        <div class="flex space-x-2">
          <input
            type="text"
            bind:value={tagInput}
            placeholder="Add a tag..."
            class="flex-1 px-3 py-2 border border-secondary-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
            on:keydown={handleTagKeydown}
          />
          <Button
            type="button"
            variant="outline"
            on:click={addTag}
            disabled={!tagInput.trim()}
          >
            Add
          </Button>
        </div>
        <p class="mt-1 text-xs text-secondary-500">
          Press Enter or click Add to include tags
        </p>
      </div>

      <!-- Submit Buttons -->
      <div class="flex justify-between items-center">
        <Button
          type="button"
          variant="outline"
          on:click={handleQuickSubmit}
          disabled={!isValid || loading}
          size="lg"
        >
          Save for Later
        </Button>
        <Button
          type="submit"
          {loading}
          disabled={!isValid}
          size="lg"
        >
          <ArrowRight size={16} class="mr-2" />
          Continue to Refinement
        </Button>
      </div>
    </form>
  </div>

  <!-- Tips -->
  <div class="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
    <h3 class="text-sm font-medium text-blue-900 mb-2">💡 Tips for better ideas</h3>
    <ul class="text-sm text-blue-800 space-y-1">
      <li>• Focus on the problem you're trying to solve</li>
      <li>• Think about who would benefit from this idea</li>
      <li>• Don't worry about technical details yet</li>
      <li>• Be specific about the outcome you want</li>
    </ul>
  </div>
</div>