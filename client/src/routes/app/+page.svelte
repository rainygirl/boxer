<script lang="ts">
  import { t } from '$lib/i18n';
  import { configStore } from '$lib/stores/config';
  import { goto } from '$app/navigation';
  import { sidebarOpen } from '$lib/stores/sidebar';

  $effect(() => {
    if ($configStore.demoMode && $configStore.demoProjectId) {
      goto(`/app/project/${$configStore.demoProjectId}`, { replaceState: true });
    }
  });
</script>

{#if !$configStore.demoMode || !$configStore.demoProjectId}
<div class="flex flex-col h-full bg-slate-50 dark:bg-slate-950">
  <header class="md:hidden flex items-center px-4 h-[60px] border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 shrink-0">
    <button
      class="p-1.5 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
      onclick={() => sidebarOpen.update((v) => !v)}
    >
      <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
      </svg>
    </button>
  </header>
  <div class="flex-1 flex flex-col items-center justify-center text-slate-400 dark:text-slate-600">
    <div class="text-6xl mb-4">📦</div>
    <p class="text-lg font-medium">{$t('app.selectProject')}</p>
  </div>
</div>
{/if}
