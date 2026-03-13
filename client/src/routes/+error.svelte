<script lang="ts">
  import { page } from '$app/stores';
  import { t } from '$lib/i18n';
</script>

<div class="min-h-screen flex flex-col items-center justify-center bg-white dark:bg-slate-900 px-4">
  {#if $page.status === 404}
    <p class="text-6xl font-bold text-slate-200 dark:text-slate-700 mb-4">404</p>
    <p class="text-xl font-semibold text-slate-500 dark:text-slate-400">Not Found</p>
    <a href="/app" class="mt-8 inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium transition-colors">{$t('common.backToBoxer')}</a>

  {:else}
    <img src="/500.gif" alt="500" class="w-64 h-64 object-contain mb-6" />
    <p class="my-4 text-xl font-semibold text-slate-500 dark:text-slate-400">500 Internal Server Error</p>
    <a href="/app" class="mt-4 inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium transition-colors">{$t('common.backToBoxer')}</a>
  {/if}
</div>
