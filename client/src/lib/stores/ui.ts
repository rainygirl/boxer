import { writable } from 'svelte/store';

export type ViewMode = 'board' | 'table';
export const viewMode = writable<ViewMode>('board');
