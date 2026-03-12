import { writable } from 'svelte/store';

const stored = typeof localStorage !== 'undefined' ? localStorage.getItem('boxer_theme') : null;
const initial = stored === 'dark' ? 'dark' : 'light';

function createThemeStore() {
  const { subscribe, set } = writable<'light' | 'dark'>(initial);

  function apply(mode: 'light' | 'dark') {
    if (typeof document !== 'undefined') {
      document.documentElement.classList.toggle('dark', mode === 'dark');
    }
    localStorage.setItem('boxer_theme', mode);
    set(mode);
  }

  return {
    subscribe,
    toggle() {
      const next = document.documentElement.classList.contains('dark') ? 'light' : 'dark';
      apply(next);
    },
    init() {
      apply(initial);
    },
  };
}

export const themeStore = createThemeStore();
