import { writable } from 'svelte/store';

export interface Toast {
  id: string;
  message: string;
  type: 'info' | 'success' | 'error';
}

function createToastStore() {
  const { subscribe, update } = writable<Toast[]>([]);

  function add(message: string, type: Toast['type'] = 'info', duration = 3500) {
    const id = crypto.randomUUID();
    update((list) => [...list, { id, message, type }]);
    setTimeout(() => remove(id), duration);
  }

  function remove(id: string) {
    update((list) => list.filter((t) => t.id !== id));
  }

  return { subscribe, add, remove };
}

export const toastStore = createToastStore();
