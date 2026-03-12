import { writable } from 'svelte/store';

// Increment to signal the current kanban board to refresh (used after cross-project moves)
export const boardRefresh = writable(0);
