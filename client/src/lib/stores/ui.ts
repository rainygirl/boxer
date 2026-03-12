import { writable } from 'svelte/store';

export type ViewMode = 'board' | 'table';

const STORAGE_KEY = 'boxer:view-mode';

function loadViewMode(): ViewMode {
  try {
    const v = localStorage.getItem(STORAGE_KEY);
    if (v === 'board' || v === 'table') return v;
  } catch {}
  return 'board';
}

export const viewMode = writable<ViewMode>(loadViewMode());

viewMode.subscribe((v) => {
  try { localStorage.setItem(STORAGE_KEY, v); } catch {}
});
