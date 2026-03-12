import { derived } from 'svelte/store';
import { localeStore } from '$lib/stores/locale';
import { ko, en } from './translations';
import type { TranslationKey } from './translations';

const dicts = { ko, en };

export { localeStore };

export const t = derived(localeStore, ($locale) => {
  const dict = dicts[$locale] ?? dicts.ko;
  return (key: TranslationKey, vars?: Record<string, string>): string => {
    let str: string = dict[key] ?? dicts.ko[key] ?? key;
    if (vars) {
      for (const [k, v] of Object.entries(vars)) {
        str = str.replace(`{${k}}`, v);
      }
    }
    return str;
  };
});

export const dateLocale = derived(
  localeStore,
  ($locale) => ($locale === 'ko' ? 'ko-KR' : 'en-US')
);
