<script lang="ts">
  import { goto, invalidate } from '$app/navigation';
  import { projectsApi } from '$lib/api/projects';
  import { t } from '$lib/i18n';

  const { onClose }: { onClose: () => void } = $props();

  const COLORS = ['#6366f1','#8b5cf6','#ec4899','#ef4444','#f97316','#eab308','#22c55e','#14b8a6','#3b82f6'];

  let name = $state('');
  let description = $state('');
  let color = $state(COLORS[0]);
  let saving = $state(false);

  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    saving = true;
    try {
      const project = await projectsApi.create({ name, description, color });
      await invalidate('app:projects');
      goto(`/app/project/${project.id}`);
      onClose();
    } finally {
      saving = false;
    }
  }
</script>

<svelte:window onkeydown={(e) => e.key === 'Escape' && onClose()} />

<div class="fixed inset-0 z-50 flex items-center justify-center">
  <div class="absolute inset-0 bg-black/30" onclick={onClose}></div>
  <div class="relative bg-white dark:bg-slate-900 rounded-2xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
    <form onsubmit={handleSubmit}>
      <div class="p-6">
        <h2 class="text-base font-semibold text-slate-800 dark:text-slate-100 mb-4">{$t('project.new')}</h2>
        <div class="space-y-3">
          <input
            autofocus
            type="text"
            bind:value={name}
            placeholder={$t('project.namePlaceholder')}
            class="w-full text-sm px-3 py-2.5 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
            required
          />
          <textarea
            bind:value={description}
            placeholder={$t('project.descriptionPlaceholder')}
            rows="2"
            class="w-full text-sm px-3 py-2.5 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent resize-none"
          ></textarea>

          <div>
            <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-2">{$t('project.color')}</label>
            <div class="flex gap-2 flex-wrap">
              {#each COLORS as c}
                <button
                  type="button"
                  onclick={() => (color = c)}
                  class="w-7 h-7 rounded-full transition-all {color === c ? 'ring-2 ring-offset-2 ring-slate-400 scale-110' : 'hover:scale-105'}"
                  style="background-color: {c}"
                ></button>
              {/each}
            </div>
          </div>

          <div class="flex items-center gap-2 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
            <span class="w-3 h-3 rounded-full" style="background-color: {color}"></span>
            <span class="text-sm font-medium text-slate-700 dark:text-slate-200">{name || $t('project.previewName')}</span>
          </div>
        </div>
      </div>

      <div class="flex items-center justify-end gap-2 px-6 py-4 bg-slate-50 dark:bg-slate-800/50 border-t border-slate-100 dark:border-slate-700">
        <button type="button" onclick={onClose} class="px-4 py-2 text-sm text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 transition-colors">
          {$t('common.cancel')}
        </button>
        <button
          type="submit"
          disabled={!name.trim() || saving}
          class="px-4 py-2 text-sm font-medium bg-brand-500 hover:bg-brand-600 text-white rounded-lg transition-colors disabled:opacity-50"
        >
          {saving ? $t('project.creating') : $t('project.create')}
        </button>
      </div>
    </form>
  </div>
</div>
