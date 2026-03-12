import { writable } from 'svelte/store';

export type Locale = 'ko' | 'en';

function createLocaleStore() {
  const initial: Locale =
    (typeof localStorage !== 'undefined' ? (localStorage.getItem('locale') as Locale) : null) ??
    'ko';
  const { subscribe, set } = writable<Locale>(initial);

  return {
    subscribe,
    set(locale: Locale) {
      if (typeof localStorage !== 'undefined') localStorage.setItem('locale', locale);
      set(locale);
    },
  };
}

export const localeStore = createLocaleStore();
