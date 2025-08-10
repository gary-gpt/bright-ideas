<script lang="ts">
  import { onMount } from 'svelte';
  import { todos, todosLoading, todosError, todoActions } from '$lib/stores/todos';
  import { toastActions } from '$lib/stores/ui';
  import LoadingSpinner from '$lib/components/shared/LoadingSpinner.svelte';
  import Button from '$lib/components/shared/Button.svelte';
  import { Plus, Check, X } from 'lucide-svelte';

  let newTodoText = '';
  let isAddingTodo = false;

  onMount(() => {
    todoActions.load();
  });

  async function handleAddTodo() {
    if (!newTodoText.trim()) return;
    
    isAddingTodo = true;
    try {
      await todoActions.create(newTodoText);
      newTodoText = '';
      toastActions.success('Todo added successfully');
    } catch (error) {
      toastActions.error('Failed to add todo');
    } finally {
      isAddingTodo = false;
    }
  }

  async function handleCompleteTodo(todoId: string, todoText: string) {
    try {
      const completedTodo = await todoActions.complete(todoId);
      
      // Show undo toast
      toastActions.successWithUndo(
        `Completed: "${todoText.length > 30 ? todoText.slice(0, 30) + '...' : todoText}"`,
        async () => {
          try {
            await todoActions.undoComplete(todoId);
            toastActions.success('Todo restored');
          } catch (error) {
            toastActions.error('Failed to undo completion');
          }
        },
        30000 // 30 seconds to undo
      );
    } catch (error) {
      toastActions.error('Failed to complete todo');
    }
  }

  async function handleDeleteTodo(todoId: string) {
    try {
      await todoActions.delete(todoId);
      toastActions.success('Todo deleted');
    } catch (error) {
      toastActions.error('Failed to delete todo');
    }
  }

  function handleKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      handleAddTodo();
    }
  }
</script>

<div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
  <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
    Quick Tasks
  </h3>

  <!-- Add new todo -->
  <div class="flex gap-2 mb-4">
    <input
      type="text"
      bind:value={newTodoText}
      on:keypress={handleKeyPress}
      placeholder="Add a new task..."
      disabled={isAddingTodo}
      class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 
             rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 
             dark:bg-gray-700 dark:text-white text-sm"
    />
    <Button
      onClick={handleAddTodo}
      disabled={!newTodoText.trim() || isAddingTodo}
      size="sm"
      variant="primary"
      class="px-3"
    >
      {#if isAddingTodo}
        <LoadingSpinner size="sm" />
      {:else}
        <Plus size={16} />
      {/if}
    </Button>
  </div>

  <!-- Loading state -->
  {#if $todosLoading}
    <div class="flex items-center justify-center py-8">
      <LoadingSpinner />
      <span class="ml-2 text-gray-600 dark:text-gray-400">Loading tasks...</span>
    </div>
  {/if}

  <!-- Error state -->
  {#if $todosError}
    <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 
                rounded-md p-3 mb-4">
      <p class="text-red-800 dark:text-red-200 text-sm">{$todosError}</p>
      <Button
        onClick={() => todoActions.clearError()}
        size="sm"
        variant="secondary"
        class="mt-2"
      >
        Dismiss
      </Button>
    </div>
  {/if}

  <!-- Todo list -->
  {#if $todos.filter(t => !t.is_completed).length === 0 && !$todosLoading}
    <div class="text-center py-8">
      <p class="text-gray-500 dark:text-gray-400">No tasks yet</p>
      <p class="text-sm text-gray-400 dark:text-gray-500 mt-1">
        Add a task above to get started
      </p>
    </div>
  {:else}
    <div class="space-y-2">
      {#each $todos.filter(t => !t.is_completed) as todo (todo.id)}
        <div class="flex items-center gap-3 p-2 bg-gray-50 dark:bg-gray-700 
                    rounded-md group hover:bg-gray-100 dark:hover:bg-gray-600 
                    transition-colors">
          <!-- Checkbox to complete -->
          <button
            on:click={() => handleCompleteTodo(todo.id, todo.text)}
            class="flex-shrink-0 w-5 h-5 border-2 border-gray-300 dark:border-gray-500 
                   rounded hover:border-green-500 hover:bg-green-50 dark:hover:bg-green-900/20
                   transition-colors flex items-center justify-center group-hover:border-green-400 {todo.is_completed ? 'bg-green-500 border-green-500' : ''}"
            title="{todo.is_completed ? 'Already completed' : 'Complete task'}"
            disabled={todo.is_completed}
          >
            <Check size={12} class="text-white {todo.is_completed ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'} transition-opacity" />
          </button>

          <!-- Todo text -->
          <span class="flex-1 text-gray-700 dark:text-gray-200 text-sm">
            {todo.text}
          </span>

          <!-- Delete button -->
          <button
            on:click={() => handleDeleteTodo(todo.id)}
            class="flex-shrink-0 w-5 h-5 text-gray-400 hover:text-red-500 
                   opacity-0 group-hover:opacity-100 transition-all"
            title="Delete task"
          >
            <X size={14} />
          </button>
        </div>
      {/each}
    </div>
  {/if}
</div>