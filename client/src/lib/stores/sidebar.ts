import { writable } from 'svelte/store';

/** Controls mobile sidebar open/close state */
export const sidebarOpen = writable(false);
