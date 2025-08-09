/**
 * Svelte store for todo management
 */
import { writable } from 'svelte/store';
import type { Todo } from '$lib/types';
import api from '$lib/services/api';

// Todo store
export const todos = writable<Todo[]>([]);
export const todosLoading = writable<boolean>(false);
export const todosError = writable<string | null>(null);

// Todo store actions
export const todoActions = {
  // Load all todos
  async load() {
    todosLoading.set(true);
    todosError.set(null);
    
    try {
      const todoList = await api.getTodos();
      todos.set(todoList);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to load todos';
      todosError.set(message);
      console.error('Failed to load todos:', error);
    } finally {
      todosLoading.set(false);
    }
  },

  // Create a new todo
  async create(text: string) {
    if (!text.trim()) return;
    
    todosError.set(null);
    
    try {
      const newTodo = await api.createTodo({ text: text.trim() });
      todos.update(current => [newTodo, ...current]);
      return newTodo;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to create todo';
      todosError.set(message);
      console.error('Failed to create todo:', error);
      throw error;
    }
  },

  // Complete a todo (this will delete it based on your spec)
  async complete(todoId: string) {
    todosError.set(null);
    
    try {
      await api.completeTodo(todoId);
      // Remove the todo from the store since it gets deleted when completed
      todos.update(current => current.filter(todo => todo.id !== todoId));
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to complete todo';
      todosError.set(message);
      console.error('Failed to complete todo:', error);
      throw error;
    }
  },

  // Update todo text (if needed)
  async update(todoId: string, text: string) {
    todosError.set(null);
    
    try {
      const updatedTodo = await api.updateTodo(todoId, { text });
      todos.update(current => 
        current.map(todo => todo.id === todoId ? updatedTodo : todo)
      );
      return updatedTodo;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to update todo';
      todosError.set(message);
      console.error('Failed to update todo:', error);
      throw error;
    }
  },

  // Delete a todo
  async delete(todoId: string) {
    todosError.set(null);
    
    try {
      await api.deleteTodo(todoId);
      todos.update(current => current.filter(todo => todo.id !== todoId));
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to delete todo';
      todosError.set(message);
      console.error('Failed to delete todo:', error);
      throw error;
    }
  },

  // Clear error
  clearError() {
    todosError.set(null);
  }
};