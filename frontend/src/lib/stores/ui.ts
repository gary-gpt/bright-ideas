/**
 * UI state management stores
 */
import { writable, derived } from 'svelte/store';
import type { Toast, LoadingState, Modal } from '$lib/types';

// Toast notifications
export const toasts = writable<Toast[]>([]);

// Loading states
export const globalLoading = writable<LoadingState>({ isLoading: false });

// Modals
export const modals = writable<Modal[]>([]);

// Navigation state
export const sidebarOpen = writable(false);
export const currentPage = writable('dashboard');

// Mobile detection
export const isMobile = writable(false);

// Theme (for future dark mode support)
export const theme = writable<'light' | 'dark'>('light');

// Search/filter panel state
export const searchPanelOpen = writable(false);

// Export modal state
export const exportModalOpen = writable(false);
export const exportLoading = writable(false);

// Derived stores
export const hasActiveToasts = derived(
  toasts,
  ($toasts) => $toasts.length > 0
);

export const openModals = derived(
  modals,
  ($modals) => $modals.filter(modal => modal.isOpen)
);

export const hasOpenModals = derived(
  openModals,
  ($openModals) => $openModals.length > 0
);

// Toast actions
export const toastActions = {
  add(toast: Omit<Toast, 'id'>) {
    const id = Math.random().toString(36).substring(2);
    const newToast: Toast = {
      id,
      duration: 5000,
      ...toast
    };

    toasts.update(items => [...items, newToast]);

    // Auto-remove after duration
    if (newToast.duration && newToast.duration > 0) {
      setTimeout(() => {
        this.remove(id);
      }, newToast.duration);
    }

    return id;
  },

  remove(id: string) {
    toasts.update(items => items.filter(item => item.id !== id));
  },

  clear() {
    toasts.set([]);
  },

  success(message: string, duration?: number) {
    return this.add({ type: 'success', message, duration });
  },

  error(message: string, duration?: number) {
    return this.add({ type: 'error', message, duration: duration || 8000 });
  },

  warning(message: string, duration?: number) {
    return this.add({ type: 'warning', message, duration });
  },

  info(message: string, duration?: number) {
    return this.add({ type: 'info', message, duration });
  }
};

// Loading actions
export const loadingActions = {
  start(message?: string) {
    globalLoading.set({ isLoading: true, message });
  },

  stop() {
    globalLoading.set({ isLoading: false });
  },

  setMessage(message: string) {
    globalLoading.update(state => ({ ...state, message }));
  }
};

// Modal actions
export const modalActions = {
  open(id: string, options: Partial<Modal> = {}) {
    modals.update(items => {
      const existing = items.find(modal => modal.id === id);
      if (existing) {
        return items.map(modal => 
          modal.id === id 
            ? { ...modal, isOpen: true, ...options }
            : modal
        );
      } else {
        return [...items, { id, isOpen: true, ...options }];
      }
    });
  },

  close(id: string) {
    modals.update(items => 
      items.map(modal => 
        modal.id === id 
          ? { ...modal, isOpen: false }
          : modal
      )
    );
  },

  closeAll() {
    modals.update(items => 
      items.map(modal => ({ ...modal, isOpen: false }))
    );
  },

  toggle(id: string, options: Partial<Modal> = {}) {
    modals.update(items => {
      const existing = items.find(modal => modal.id === id);
      if (existing) {
        return items.map(modal => 
          modal.id === id 
            ? { ...modal, isOpen: !modal.isOpen, ...options }
            : modal
        );
      } else {
        return [...items, { id, isOpen: true, ...options }];
      }
    });
  }
};

// Navigation actions
export const navigationActions = {
  toggleSidebar() {
    sidebarOpen.update(open => !open);
  },

  closeSidebar() {
    sidebarOpen.set(false);
  },

  openSidebar() {
    sidebarOpen.set(true);
  },

  setCurrentPage(page: string) {
    currentPage.set(page);
  }
};

// Mobile detection setup
if (typeof window !== 'undefined') {
  const checkMobile = () => {
    isMobile.set(window.innerWidth < 768);
  };
  
  checkMobile();
  window.addEventListener('resize', checkMobile);
}

// Keyboard shortcuts
if (typeof window !== 'undefined') {
  window.addEventListener('keydown', (event) => {
    // ESC key - close modals
    if (event.key === 'Escape') {
      modalActions.closeAll();
      navigationActions.closeSidebar();
      searchPanelOpen.set(false);
    }
    
    // Cmd/Ctrl + K - open search
    if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
      event.preventDefault();
      searchPanelOpen.update(open => !open);
    }
  });
}

// Export actions
export const exportActions = {
  openModal() {
    exportModalOpen.set(true);
  },

  closeModal() {
    exportModalOpen.set(false);
  },

  setLoading(loading: boolean) {
    exportLoading.set(loading);
  }
};