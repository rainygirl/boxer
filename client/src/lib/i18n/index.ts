import { derived } from 'svelte/store';
import { localeStore } from '$lib/stores/locale';
import { ko, en, ja, zhHans, zhHant, yue, es, fr, vi, id } from './translations';
import type { TranslationKey } from './translations';

const dicts: Record<string, typeof ko> = { ko, en, ja, 'zh-Hans': zhHans, 'zh-Hant': zhHant, yue, es, fr, vi, id };

export { localeStore };

export const t = derived(localeStore, ($locale) => {
  const dict = dicts[$locale] ?? dicts.en;
  return (key: TranslationKey, vars?: Record<string, string>): string => {
    let str: string = dict[key] ?? dicts.en[key] ?? key;
    if (vars) {
      for (const [k, v] of Object.entries(vars)) {
        str = str.replace(`{${k}}`, v);
      }
    }
    return str;
  };
});

export const dateLocale = derived(localeStore, ($locale) => {
  const map: Record<string, string> = {
    ko: 'ko-KR',
    en: 'en-US',
    ja: 'ja-JP',
    'zh-Hans': 'zh-CN',
    'zh-Hant': 'zh-TW',
    yue: 'zh-HK',
    es: 'es-ES',
    fr: 'fr-FR',
    vi: 'vi-VN',
    id: 'id-ID',
  };
  return map[$locale] ?? 'en-US';
});
