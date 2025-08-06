<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { api } from '$lib/services/api';
  import Button from '$lib/components/shared/Button.svelte';
  import Modal from '$lib/components/shared/Modal.svelte';
  import { addToast } from '$lib/stores/ui';
  import type { Plan } from '$lib/types';

  export let ideaId: string;
  export let show = false;

  const dispatch = createEventDispatcher<{
    uploaded: Plan;
    close: void;
  }>();

  let content = '';
  let title = '';
  let uploading = false;
  let previewMode = false;

  // Preview parsing
  let previewSummary = '';
  let previewSteps: any[] = [];
  let previewResources: any[] = [];

  $: {
    if (previewMode && content) {
      parsePreview(content);
    }
  }

  function parsePreview(text: string) {
    // Simple preview parsing (client-side approximation)
    const lines = text.split('\n');
    
    previewSummary = '';
    previewSteps = [];
    previewResources = [];
    
    let currentSection = null;
    let stepOrder = 1;
    
    for (let line of lines) {
      line = line.trim();
      if (!line) continue;
      
      if (line.startsWith('##')) {
        const header = line.toLowerCase();
        if (header.includes('summary')) {
          currentSection = 'summary';
        } else if (header.includes('step') || header.includes('plan') || header.includes('implementation')) {
          currentSection = 'steps';
        } else if (header.includes('resource') || header.includes('tool')) {
          currentSection = 'resources';
        } else {
          currentSection = null;
        }
      } else if (currentSection === 'summary' && !previewSummary) {
        previewSummary = line;
      } else if (currentSection === 'steps') {
        // Look for numbered or bulleted items
        const stepMatch = line.match(/^(?:\d+\.\s*|[-*]\s*)(.+)/);
        if (stepMatch) {
          const [title, ...descParts] = stepMatch[1].split(' - ');
          previewSteps.push({
            order: stepOrder++,
            title: title.trim(),
            description: descParts.join(' - ').trim() || 'Step description'
          });
        }
      } else if (currentSection === 'resources') {
        const resourceMatch = line.match(/^[-*]\s*(.+)/);
        if (resourceMatch) {
          const [title, ...descParts] = resourceMatch[1].split(' - ');
          previewResources.push({
            title: title.trim(),
            description: descParts.join(' - ').trim() || ''
          });
        }
      }
    }
    
    // Generate default summary if missing
    if (!previewSummary && previewSteps.length > 0) {
      previewSummary = `Implementation plan with ${previewSteps.length} steps.`;
    } else if (!previewSummary) {
      previewSummary = 'Uploaded implementation plan.';
    }
  }

  async function handleUpload() {
    if (!content.trim()) {
      addToast('Please enter plan content', 'error');
      return;
    }

    uploading = true;
    try {
      const uploadedPlan = await api.uploadPlan({
        idea_id: ideaId,
        content: content.trim(),
        title: title.trim() || undefined
      });

      addToast('Plan uploaded successfully!', 'success');
      dispatch('uploaded', uploadedPlan);
      handleClose();
    } catch (error) {
      console.error('Upload failed:', error);
      addToast('Failed to upload plan. Please try again.', 'error');
    } finally {
      uploading = false;
    }
  }

  function handleClose() {
    show = false;
    content = '';
    title = '';
    previewMode = false;
    dispatch('close');
  }

  function togglePreview() {
    previewMode = !previewMode;
  }

  // Example content to help users
  const exampleContent = `## Summary
This is a tool to scrape and summarize RV blog content for research purposes.

## Implementation Steps
1. Setup Scrapy Project - Install scrapy, create project structure (30 minutes)
2. Build Blog Spider - Create spider to crawl RV blog sites, extract articles (2-3 days)
3. Content Processing - Add text cleaning and deduplication logic (1 day)
4. OpenAI Integration - Implement summarization using GPT-4 API (1 day)
5. Storage Layer - Setup SQLite database with proper indexing (1 day)
6. CLI Interface - Add command-line interface for running scrapes (1 day)

## Resources
- Scrapy Framework - Web scraping framework for Python
- OpenAI API - For content summarization
- SQLite - Local database for storing articles`;

  function insertExample() {
    content = exampleContent;
  }
</script>

<Modal bind:show={show} title="Upload Implementation Plan" size="large" on:close={handleClose}>
  <div class="space-y-6">
    <!-- Title input -->
    <div>
      <label for="plan-title" class="block text-sm font-medium text-gray-700 mb-2">
        Plan Title (Optional)
      </label>
      <input
        id="plan-title"
        type="text"
        bind:value={title}
        placeholder="Leave empty to use idea title"
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
      />
    </div>

    <!-- Content input with tabs -->
    <div>
      <div class="flex items-center justify-between mb-2">
        <label for="plan-content" class="block text-sm font-medium text-gray-700">
          Plan Content
        </label>
        <div class="flex items-center space-x-2">
          <button
            type="button"
            on:click={insertExample}
            class="text-sm text-blue-600 hover:text-blue-800 hover:underline"
          >
            Insert Example
          </button>
          <Button size="sm" variant="outline" on:click={togglePreview}>
            {previewMode ? 'Edit' : 'Preview'}
          </Button>
        </div>
      </div>

      {#if previewMode}
        <!-- Preview mode -->
        <div class="border border-gray-300 rounded-md p-4 bg-gray-50 max-h-96 overflow-y-auto">
          <div class="space-y-4">
            <!-- Summary preview -->
            <div>
              <h4 class="text-sm font-medium text-gray-700 mb-1">Summary</h4>
              <p class="text-sm text-gray-600">{previewSummary}</p>
            </div>

            <!-- Steps preview -->
            {#if previewSteps.length > 0}
              <div>
                <h4 class="text-sm font-medium text-gray-700 mb-2">Steps ({previewSteps.length})</h4>
                <div class="space-y-2">
                  {#each previewSteps as step}
                    <div class="flex items-start space-x-2 text-sm">
                      <span class="flex-shrink-0 w-5 h-5 bg-blue-100 rounded-full flex items-center justify-center text-xs font-medium text-blue-600">
                        {step.order}
                      </span>
                      <div>
                        <div class="font-medium text-gray-900">{step.title}</div>
                        {#if step.description}
                          <div class="text-gray-600">{step.description}</div>
                        {/if}
                      </div>
                    </div>
                  {/each}
                </div>
              </div>
            {/if}

            <!-- Resources preview -->
            {#if previewResources.length > 0}
              <div>
                <h4 class="text-sm font-medium text-gray-700 mb-2">Resources ({previewResources.length})</h4>
                <div class="space-y-1">
                  {#each previewResources as resource}
                    <div class="text-sm">
                      <span class="font-medium text-gray-900">{resource.title}</span>
                      {#if resource.description}
                        <span class="text-gray-600"> - {resource.description}</span>
                      {/if}
                    </div>
                  {/each}
                </div>
              </div>
            {/if}
          </div>
        </div>
      {:else}
        <!-- Edit mode -->
        <textarea
          id="plan-content"
          bind:value={content}
          placeholder="Paste your implementation plan here...

Supports:
• Markdown format with ## headers
• Numbered or bulleted lists for steps
• Resource lists with - bullets
• Links in [title](url) format"
          rows="16"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 font-mono text-sm"
        ></textarea>
      {/if}
    </div>

    <!-- Help text -->
    <div class="bg-blue-50 p-3 rounded-md">
      <div class="text-xs text-blue-800">
        <strong>Tip:</strong> Copy your ChatGPT-generated plan and paste it here. The system will automatically parse sections like "Summary", "Steps", and "Resources" to create a structured plan.
      </div>
    </div>
  </div>

  <svelte:fragment slot="footer">
    <div class="flex justify-end space-x-3">
      <Button variant="outline" on:click={handleClose} disabled={uploading}>
        Cancel
      </Button>
      <Button on:click={handleUpload} loading={uploading}>
        Upload Plan
      </Button>
    </div>
  </svelte:fragment>
</Modal>