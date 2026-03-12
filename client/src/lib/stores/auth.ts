import { writable } from 'svelte/store';
import type { User } from '$lib/types';

function createAuthStore() {
  const { subscribe, set, update } = writable<{
    token: string | null;
    user: User | null;
  }>({
    token: typeof localStorage !== 'undefined' ? localStorage.getItem('boxer_token') : null,
    user: null,
  });

  return {
    subscribe,
    setToken(token: string) {
      localStorage.setItem('boxer_token', token);
      update((s) => ({ ...s, token }));
    },
    setUser(user: User) {
      update((s) => ({ ...s, user }));
    },
    logout() {
      localStorage.removeItem('boxer_token');
      set({ token: null, user: null });
    },
  };
}

export const authStore = createAuthStore();
