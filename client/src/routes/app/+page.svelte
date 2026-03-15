<script lang="ts">
  import { t } from '$lib/i18n';
  import { configStore } from '$lib/stores/config';
  import { goto } from '$app/navigation';

  $effect(() => {
    if ($configStore.demoMode && $configStore.demoProjectId) {
      goto(`/app/project/${$configStore.demoProjectId}`, { replaceState: true });
    }
  });
</script>

{#if !$configStore.demoMode || !$configStore.demoProjectId}
<div class="flex flex-col items-center justify-center h-full text-slate-400 dark:text-slate-600 bg-slate-50 dark:bg-slate-950">
  <div class="text-6xl mb-4">📦</div>
  <p class="text-lg font-medium">{$t('app.selectProject')}</p>
</div>
{/if}
