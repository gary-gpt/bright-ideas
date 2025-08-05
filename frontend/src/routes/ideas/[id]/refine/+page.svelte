<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { ideaActions } from '$lib/stores';
  import { toastActions } from '$lib/stores';
  import { api } from '$lib/services/api';
  import Button from '$lib/components/shared/Button.svelte';
  import LoadingSpinner from '$lib/components/shared/LoadingSpinner.svelte';
  import type { Idea, Conversation, ChatMessage } from '$lib/types';

  let idea: Idea | null = null;
  let conversation: Conversation | null = null;
  let loading = true;
  let refining = false;
  let messages: ChatMessage[] = [];
  let userMessage = '';
  let chatContainer: HTMLElement;

  $: ideaId = $page.params.id;

  onMount(async () => {
    if (ideaId) {
      try {
        // Load the idea
        idea = await ideaActions.loadIdea(ideaId);
        
        // Try to load existing conversation or start new one
        await loadOrStartConversation();
      } catch (error) {
        console.error('Failed to load idea or conversation:', error);
        toastActions.error('Failed to load refinement session');
        goto(`/ideas/${ideaId}`);
      } finally {
        loading = false;
      }
    }
  });

  async function loadOrStartConversation() {
    if (!ideaId) return;

    try {
      // Check if there's an existing refinement conversation
      const conversations = await api.getIdeaConversations(ideaId, 'capture');
      
      if (conversations.length > 0) {
        conversation = conversations[0];
        messages = conversation.messages;
      } else {
        // Start a new refinement conversation
        conversation = await api.startRefinementConversation(ideaId);
        messages = conversation.messages;
      }
    } catch (error) {
      console.error('Failed to load/start conversation:', error);
      throw error;
    }
  }

  async function sendMessage() {
    if (!userMessage.trim() || !conversation || refining) return;

    const currentMessage = userMessage.trim();
    userMessage = '';
    refining = true;

    try {
      // Add user message to display immediately
      messages = [...messages, {
        role: 'user',
        content: currentMessage,
        timestamp: new Date().toISOString()
      }];

      // Scroll to bottom
      setTimeout(() => {
        if (chatContainer) {
          chatContainer.scrollTop = chatContainer.scrollHeight;
        }
      }, 10);

      // Send to API and get AI response
      const response = await api.chat({
        message: currentMessage,
        conversation_id: conversation.id,
        context: { idea_id: ideaId }
      });

      // Add AI response
      messages = [...messages, {
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString()
      }];

      // Update conversation
      conversation.messages = messages;

      // Reload idea to get any updates from AI
      if (idea) {
        idea = await ideaActions.loadIdea(ideaId);
      }

      // Scroll to bottom again
      setTimeout(() => {
        if (chatContainer) {
          chatContainer.scrollTop = chatContainer.scrollHeight;
        }
      }, 10);

    } catch (error) {
      console.error('Failed to send message:', error);
      toastActions.error('Failed to send message. Please try again.');
    } finally {
      refining = false;
    }
  }

  function handleKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  function formatTime(timestamp: string): string {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    });
  }
</script>

<svelte:head>
  <title>Refine: {idea ? idea.title : 'Loading...'} - Bright Ideas</title>
</svelte:head>

<div class="min-h-screen bg-secondary-50">
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="mb-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <Button variant="ghost" href="/ideas/{ideaId}" size="sm">
            ← Back to Idea
          </Button>
          <div>
            <h1 class="text-2xl font-bold text-secondary-900">
              AI Refinement Session
            </h1>
            {#if idea}
              <p class="text-secondary-600">{idea.title}</p>
            {/if}
          </div>
        </div>
      </div>
    </div>

    {#if loading}
      <div class="flex justify-center py-12">
        <LoadingSpinner size="lg" message="Loading refinement session..." />
      </div>
    {:else if idea && conversation}
      <div class="bg-white rounded-lg shadow-sm border border-secondary-200 h-[600px] flex flex-col">
        <!-- Chat Messages -->
        <div 
          bind:this={chatContainer}
          class="flex-1 overflow-y-auto p-6 space-y-4"
        >
          {#each messages as message}
            <div class="flex {message.role === 'user' ? 'justify-end' : 'justify-start'}">
              <div class="max-w-[80%]">
                <div class="flex items-center space-x-2 mb-1">
                  <span class="text-xs font-medium {message.role === 'user' ? 'text-primary-600' : 'text-secondary-600'}">
                    {message.role === 'user' ? 'You' : 'AI Assistant'}
                  </span>
                  <span class="text-xs text-secondary-400">
                    {formatTime(message.timestamp)}
                  </span>
                </div>
                <div class="rounded-lg p-3 {message.role === 'user' ? 'bg-primary-600 text-white' : 'bg-secondary-100 text-secondary-900'}">
                  <div class="whitespace-pre-wrap">{message.content}</div>
                </div>
              </div>
            </div>
          {/each}

          {#if refining}
            <div class="flex justify-start">
              <div class="max-w-[80%]">
                <div class="flex items-center space-x-2 mb-1">
                  <span class="text-xs font-medium text-secondary-600">AI Assistant</span>
                  <span class="text-xs text-secondary-400">thinking...</span>
                </div>
                <div class="rounded-lg p-3 bg-secondary-100 text-secondary-900">
                  <LoadingSpinner size="sm" message="Generating response..." />
                </div>
              </div>
            </div>
          {/if}
        </div>

        <!-- Message Input -->
        <div class="border-t border-secondary-200 p-4">
          <div class="flex space-x-3">
            <div class="flex-1">
              <textarea
                bind:value={userMessage}
                on:keypress={handleKeyPress}
                placeholder="Ask the AI to help refine your idea, identify problems, define target audience, or plan implementation..."
                class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
                rows="3"
                disabled={refining}
              ></textarea>
            </div>
            <div class="flex flex-col justify-end">
              <Button 
                on:click={sendMessage} 
                disabled={!userMessage.trim() || refining}
                loading={refining}
                size="sm"
              >
                Send
              </Button>
            </div>
          </div>
          <div class="mt-2 text-xs text-secondary-500">
            Press Enter to send, Shift+Enter for new line
          </div>
        </div>
      </div>

      <!-- Idea Status -->
      <div class="mt-6 bg-white rounded-lg shadow-sm border border-secondary-200 p-6">
        <h3 class="text-lg font-semibold text-secondary-900 mb-4">Current Idea Status</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-secondary-700 mb-1">Status</label>
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              {idea.status}
            </span>
          </div>
          <div>
            <label class="block text-sm font-medium text-secondary-700 mb-1">Last Updated</label>
            <span class="text-sm text-secondary-600">
              {new Date(idea.updated_at).toLocaleString()}
            </span>
          </div>
          {#if idea.refined_description}
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-secondary-700 mb-1">Latest Refined Description</label>
              <p class="text-sm text-secondary-600">{idea.refined_description}</p>
            </div>
          {/if}
        </div>
      </div>
    {:else}
      <div class="text-center py-12">
        <h2 class="text-xl font-bold text-secondary-900 mb-2">Unable to Start Refinement</h2>
        <p class="text-secondary-600 mb-4">There was an issue loading the refinement session.</p>
        <Button href="/ideas/{ideaId}">Back to Idea</Button>
      </div>
    {/if}
  </div>
</div>