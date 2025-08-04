/**
 * Svelte stores for conversation management
 */
import { writable, derived } from 'svelte/store';
import type { Conversation, ChatMessage } from '$lib/types';
import { api } from '$lib/services/api';

// Conversation stores
export const conversations = writable<Conversation[]>([]);
export const currentConversation = writable<Conversation | null>(null);
export const conversationLoading = writable(false);
export const messageLoading = writable(false);

// Chat state
export const isTyping = writable(false);
export const chatInput = writable('');

// Derived stores
export const currentMessages = derived(
  currentConversation,
  ($conversation) => $conversation?.messages || []
);

export const conversationsByMode = derived(
  conversations,
  ($conversations) => {
    const byMode: Record<string, Conversation[]> = {
      capture: [],
      build: []
    };

    $conversations.forEach(conv => {
      byMode[conv.mode].push(conv);
    });

    return byMode;
  }
);

export const latestMessage = derived(
  currentMessages,
  ($messages) => $messages[$messages.length - 1] || null
);

// Actions
export const conversationActions = {
  async loadConversations(ideaId: string, mode?: string) {
    conversationLoading.set(true);
    try {
      const loadedConversations = await api.getIdeaConversations(ideaId, mode);
      conversations.set(loadedConversations);
      return loadedConversations;
    } catch (error) {
      console.error('Failed to load conversations:', error);
      throw error;
    } finally {
      conversationLoading.set(false);
    }
  },

  async loadConversation(conversationId: string) {
    conversationLoading.set(true);
    try {
      const conversation = await api.getConversation(conversationId);
      currentConversation.set(conversation);
      return conversation;
    } catch (error) {
      console.error('Failed to load conversation:', error);
      throw error;
    } finally {
      conversationLoading.set(false);
    }
  },

  async createConversation(ideaId: string, mode: 'capture' | 'build', initialMessage?: string) {
    try {
      const newConversation = await api.createConversation({
        idea_id: ideaId,
        mode,
        initial_message: initialMessage
      });
      
      conversations.update(items => [newConversation, ...items]);
      currentConversation.set(newConversation);
      
      return newConversation;
    } catch (error) {
      console.error('Failed to create conversation:', error);
      throw error;
    }
  },

  async startRefinementConversation(ideaId: string) {
    conversationLoading.set(true);
    try {
      const conversation = await api.startRefinementConversation(ideaId);
      
      conversations.update(items => [conversation, ...items]);
      currentConversation.set(conversation);
      
      return conversation;
    } catch (error) {
      console.error('Failed to start refinement conversation:', error);
      throw error;
    } finally {
      conversationLoading.set(false);
    }
  },

  async sendMessage(conversationId: string, content: string) {
    if (!content.trim()) return;

    messageLoading.set(true);
    isTyping.set(true);

    try {
      // Add user message immediately for better UX
      const userMessage: ChatMessage = {
        role: 'user',
        content: content.trim(),
        timestamp: new Date().toISOString()
      };

      currentConversation.update(conv => {
        if (conv && conv.id === conversationId) {
          return {
            ...conv,
            messages: [...conv.messages, userMessage]
          };
        }
        return conv;
      });

      // Send message to API
      const updatedConversation = await api.addMessage(conversationId, {
        role: 'user',
        content: content.trim()
      });

      // Update with server response
      currentConversation.set(updatedConversation);
      
      // Update in conversations list
      conversations.update(items => 
        items.map(item => item.id === conversationId ? updatedConversation : item)
      );

      // Clear chat input
      chatInput.set('');
      
      return updatedConversation;
    } catch (error) {
      console.error('Failed to send message:', error);
      throw error;
    } finally {
      messageLoading.set(false);
      isTyping.set(false);
    }
  },

  async updateContext(conversationId: string, contextUpdates: Record<string, any>) {
    try {
      await api.updateConversationContext(conversationId, contextUpdates);
      
      // Update local conversation
      currentConversation.update(conv => {
        if (conv && conv.id === conversationId) {
          return {
            ...conv,
            context: { ...conv.context, ...contextUpdates }
          };
        }
        return conv;
      });
    } catch (error) {
      console.error('Failed to update conversation context:', error);
      throw error;
    }
  },

  async deleteConversation(conversationId: string) {
    try {
      await api.deleteConversation(conversationId);
      
      // Remove from conversations list
      conversations.update(items => 
        items.filter(item => item.id !== conversationId)
      );
      
      // Clear current conversation if it matches
      currentConversation.update(current => 
        current?.id === conversationId ? null : current
      );
    } catch (error) {
      console.error('Failed to delete conversation:', error);
      throw error;
    }
  },

  // UI actions
  setTyping(typing: boolean) {
    isTyping.set(typing);
  },

  setChatInput(input: string) {
    chatInput.set(input);
  },

  clearCurrentConversation() {
    currentConversation.set(null);
  },

  // Helper to get conversation by ID
  async ensureConversationLoaded(conversationId: string) {
    const current = currentConversation;
    let conv: Conversation | null = null;
    
    current.subscribe(c => conv = c)();
    
    if (!conv || conv.id !== conversationId) {
      return await this.loadConversation(conversationId);
    }
    
    return conv;
  }
};