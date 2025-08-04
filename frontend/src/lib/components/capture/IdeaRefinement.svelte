<script lang="ts">
  /**
   * AI-powered idea refinement chat interface
   */
  import { createEventDispatcher } from 'svelte';
  import { Send, Bot, User } from 'lucide-svelte';
  import Button from '$lib/components/shared/Button.svelte';
  import LoadingSpinner from '$lib/components/shared/LoadingSpinner.svelte';
  import type { Conversation, ChatMessage } from '$lib/types';

  export let conversation: Conversation;
  export let loading = false;
  export let messageLoading = false;

  const dispatch = createEventDispatcher<{ 
    sendMessage: string;
    updateIdea: any;
    finishRefinement: void;
  }>();

  let messageInput = '';
  let messagesContainer: HTMLDivElement;

  $: if (messagesContainer && conversation.messages.length > 0) {
    setTimeout(() => {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 100);
  }

  function handleSendMessage() {
    const message = messageInput.trim();
    if (message && !messageLoading) {
      dispatch('sendMessage', message);
      messageInput = '';
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  }

  function formatTimestamp(timestamp: string): string {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  }

  function hasQuestions(message: ChatMessage): boolean {
    return message.metadata?.questions && message.metadata.questions.length > 0;
  }

  function selectSuggestedQuestion(question: string) {
    messageInput = question;
  }
</script>

<div class="flex flex-col h-full max-w-4xl mx-auto bg-white rounded-lg shadow-sm border border-secondary-200">
  <!-- Header -->
  <div class="flex items-center justify-between p-4 border-b border-secondary-200 bg-secondary-50 rounded-t-lg">
    <div class="flex items-center space-x-3">
      <div class="flex-shrink-0 p-2 bg-primary-100 rounded-lg">
        <Bot size={20} class="text-primary-600" />
      </div>
      <div>
        <h2 class="text-lg font-semibold text-secondary-900">Idea Refinement</h2>
        <p class="text-xs text-secondary-600">
          Let's explore and improve your concept together
        </p>
      </div>
    </div>
    <Button
      variant="outline"
      size="sm"
      on:click={() => dispatch('finishRefinement')}
    >
      Finish Refinement
    </Button>
  </div>

  <!-- Messages -->
  <div
    bind:this={messagesContainer}
    class="flex-1 overflow-y-auto p-4 space-y-4 min-h-0"
  >
    {#if loading}
      <div class="flex justify-center py-8">
        <LoadingSpinner message="Starting conversation..." />
      </div>
    {:else}
      {#each conversation.messages as message}
        <div class="flex {message.role === 'user' ? 'justify-end' : 'justify-start'}">
          <div class="flex max-w-xs lg:max-w-md space-x-3 {message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}">
            <!-- Avatar -->
            <div class="flex-shrink-0">
              <div class="w-8 h-8 rounded-full flex items-center justify-center {message.role === 'user' ? 'bg-primary-100' : 'bg-secondary-100'}">
                {#if message.role === 'user'}
                  <User size={16} class="text-primary-600" />
                {:else}
                  <Bot size={16} class="text-secondary-600" />
                {/if}
              </div>
            </div>

            <!-- Message bubble -->
            <div class="relative">
              <div class="px-4 py-2 rounded-lg {message.role === 'user' ? 'bg-primary-600 text-white' : 'bg-secondary-100 text-secondary-900'}">
                <p class="text-sm whitespace-pre-wrap">{message.content}</p>
              </div>
              <p class="text-xs text-secondary-500 mt-1 {message.role === 'user' ? 'text-right' : 'text-left'}">
                {formatTimestamp(message.timestamp)}
              </p>

              <!-- Suggested questions -->
              {#if message.role === 'assistant' && hasQuestions(message)}
                <div class="mt-3 space-y-2">
                  <p class="text-xs font-medium text-secondary-600">Suggested questions:</p>
                  {#each message.metadata.questions as question}
                    <button
                      type="button"
                      class="block w-full text-left px-3 py-2 text-xs bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-md text-blue-800 transition-colors"
                      on:click={() => selectSuggestedQuestion(question)}
                    >
                      {question}
                    </button>
                  {/each}
                </div>
              {/if}
            </div>
          </div>
        </div>
      {/each}

      <!-- Typing indicator -->
      {#if messageLoading}
        <div class="flex justify-start">
          <div class="flex space-x-3">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 rounded-full bg-secondary-100 flex items-center justify-center">
                <Bot size={16} class="text-secondary-600" />
              </div>
            </div>
            <div class="bg-secondary-100 rounded-lg px-4 py-2">
              <div class="flex space-x-1">
                <div class="w-2 h-2 bg-secondary-400 rounded-full animate-bounce" style="animation-delay: 0ms" />
                <div class="w-2 h-2 bg-secondary-400 rounded-full animate-bounce" style="animation-delay: 150ms" />
                <div class="w-2 h-2 bg-secondary-400 rounded-full animate-bounce" style="animation-delay: 300ms" />
              </div>
            </div>
          </div>
        </div>
      {/if}
    {/if}
  </div>

  <!-- Input -->
  <div class="p-4 border-t border-secondary-200">
    <div class="flex space-x-3">
      <div class="flex-1">
        <textarea
          bind:value={messageInput}
          placeholder="Ask a question or share more details about your idea..."
          rows="2"
          class="w-full px-3 py-2 border border-secondary-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 resize-none"
          on:keydown={handleKeydown}
          disabled={messageLoading}
        />
      </div>
      <div class="flex-shrink-0">
        <Button
          on:click={handleSendMessage}
          disabled={!messageInput.trim() || messageLoading}
          loading={messageLoading}
        >
          <Send size={16} />
        </Button>
      </div>
    </div>
    <p class="text-xs text-secondary-500 mt-2">
      Press Enter to send, Shift+Enter for new line
    </p>
  </div>
</div>