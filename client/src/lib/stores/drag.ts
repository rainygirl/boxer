import { writable } from 'svelte/store';
import type { Task } from '$lib/types';

// The task currently being dragged (set on drag start, cleared on drop)
export const draggingTask = writable<Task | null>(null);

// The sidebar project id the pointer is currently hovering over during a drag
export const sidebarHoverProjectId = writable<string | null>(null);
