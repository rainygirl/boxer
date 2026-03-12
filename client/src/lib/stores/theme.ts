import { writable } from 'svelte/store';

export type Theme = 'light' | 'blue' | 'dark';
const ORDER: Theme[] = ['light', 'blue', 'dark'];

const stored = typeof localStorage !== 'undefined' ? localStorage.getItem('boxer_theme') : null;
const initial: Theme = (ORDER.includes(stored as Theme) ? stored : 'light') as Theme;

function createThemeStore() {
  const { subscribe, set } = writable<Theme>(initial);

  function apply(theme: Theme) {
    if (typeof document !== 'undefined') {
      document.documentElement.classList.add('no-transitions');
      document.documentElement.classList.toggle('dark', theme === 'blue' || theme === 'dark');
      document.documentElement.classList.toggle('theme-black', theme === 'dark');
      requestAnimationFrame(() =>
        requestAnimationFrame(() =>
          document.documentElement.classList.remove('no-transitions')
        )
      );
    }
    localStorage.setItem('boxer_theme', theme);
    set(theme);
  }

  return {
    subscribe,
    toggle() {
      const cur = ORDER.indexOf(initial);
      // read current from DOM to be accurate
      const curTheme: Theme = document.documentElement.classList.contains('theme-black')
        ? 'dark'
        : document.documentElement.classList.contains('dark')
        ? 'blue'
        : 'light';
      const next = ORDER[(ORDER.indexOf(curTheme) + 1) % ORDER.length];
      apply(next);
    },
    init() {
      apply(initial);
    },
  };
}

export const themeStore = createThemeStore();
