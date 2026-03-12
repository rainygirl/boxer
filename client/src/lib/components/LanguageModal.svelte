<script lang="ts">
  import { localeStore } from '$lib/stores/locale';
  import { LANGUAGES } from '$lib/i18n/translations';
  import { t } from '$lib/i18n';
  import type { Locale } from '$lib/stores/locale';

  const { onClose }: { onClose: () => void } = $props();

  function select(code: string) {
    localeStore.set(code as Locale);
    onClose();
  }

  function handleBackdrop(e: MouseEvent) {
    if (e.target === e.currentTarget) onClose();
  }
</script>

<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
<div
  role="dialog"
  class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
  onclick={handleBackdrop}
  onkeydown={(e) => { if (e.key === 'Escape') onClose(); }}
>
  <div class="bg-white dark:bg-slate-900 rounded-2xl shadow-2xl w-[420px] max-w-[calc(100vw-2rem)] overflow-hidden">
    <!-- Header -->
    <div class="flex items-center justify-between px-5 py-4 border-b border-slate-100 dark:border-slate-700">
      <h2 class="text-base font-semibold text-slate-800 dark:text-slate-100">{$t('sidebar.language')}</h2>
      <button
        onclick={onClose}
        class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 text-lg leading-none transition-colors"
      >✕</button>
    </div>

    <!-- Language grid -->
    <div class="p-4 grid grid-cols-2 gap-2">
      {#each LANGUAGES as lang (lang.code)}
        {@const isActive = $localeStore === lang.code}
        <button
          onclick={() => select(lang.code)}
          class="flex flex-col items-start gap-0.5 px-4 py-3 rounded-xl border transition-all text-left
            {isActive
              ? 'border-brand-500 bg-brand-50 dark:bg-brand-900/30 ring-2 ring-brand-400 dark:ring-brand-500'
              : 'border-slate-200 dark:border-slate-700 hover:border-brand-300 dark:hover:border-brand-600 hover:bg-slate-50 dark:hover:bg-slate-800'}"
        >
          <span class="text-sm font-semibold {isActive ? 'text-brand-700 dark:text-brand-300' : 'text-slate-700 dark:text-slate-200'}">{lang.native}</span>
          <span class="text-xs {isActive ? 'text-brand-500 dark:text-brand-400' : 'text-slate-400 dark:text-slate-500'}">{lang.english}</span>
        </button>
      {/each}
    </div>
  </div>
</div>
