<script lang="ts">
  import { goto, invalidate } from '$app/navigation';
  import { projectsApi } from '$lib/api/projects';
  import { t } from '$lib/i18n';

  const { onClose }: { onClose: () => void } = $props();

  const COLORS = ['#6366f1','#8b5cf6','#ec4899','#ef4444','#f97316','#eab308','#22c55e','#14b8a6','#3b82f6'];

  let name = $state('');
  let description = $state('');
  let color = $state(COLORS[0]);
  let key = $state('');
  let keyError = $state('');
  let visibility = $state<'public' | 'private'>('private');
  let saving = $state(false);

  function validateKey(v: string) {
    if (!v) return '';
    if (!/^[A-Za-z]{1,20}$/.test(v)) return $t('project.keyValidation');
    return '';
  }

  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    const trimmedKey = key.trim().toUpperCase();
    keyError = validateKey(trimmedKey);
    if (keyError) return;
    saving = true;
    try {
      const project = await projectsApi.create({
        name, description, color, visibility,
        ...(trimmedKey ? { key: trimmedKey } : {}),
      });
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
  <div class="absolute inset-0 bg-black/60" onclick={onClose}></div>
  <div class="relative bg-white dark:bg-slate-900 rounded-2xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
    <form onsubmit={handleSubmit}>
      <div class="flex items-center justify-between px-6 pt-5 pb-0">
        <h2 class="text-base font-semibold text-slate-800 dark:text-slate-100">{$t('project.new')}</h2>
        <button type="button" onclick={onClose} class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 w-7 h-7 flex items-center justify-center rounded hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">✕</button>
      </div>
      <div class="p-6">
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

          <!-- Visibility -->
          <div>
            <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1.5">{$t('project.visibility')}</label>
            <div class="grid grid-cols-2 gap-2">
              {#each (['public', 'private'] as const) as v}
                <button
                  type="button"
                  onclick={() => (visibility = v)}
                  class="flex flex-col items-start gap-0.5 p-2.5 rounded-lg border text-left transition-all
                    {visibility === v
                      ? 'border-brand-500 bg-brand-50 dark:bg-brand-500/20 dark:border-brand-400'
                      : 'border-slate-200 dark:border-slate-600 hover:border-slate-300 dark:hover:border-slate-500'}"
                >
                  <span class="text-base leading-none">{v === 'public' ? '🌐' : '🔒'}</span>
                  <span class="text-xs font-medium text-slate-700 dark:text-slate-200 mt-1">{$t(`project.visibility${v === 'public' ? 'Public' : 'Private'}`)}</span>
                  <span class="text-[10px] text-slate-400 dark:text-slate-500 leading-tight">{$t(`project.visibility${v === 'public' ? 'Public' : 'Private'}Desc`)}</span>
                </button>
              {/each}
            </div>
          </div>

          <!-- Project Key -->
          <div>
            <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">
              {$t('project.keyLabel')} <span class="font-normal text-slate-400">{$t('project.keyOptionalHint')}</span>
            </label>
            <div class="flex items-center gap-2">
              <input
                type="text"
                bind:value={key}
                oninput={() => { key = key.toUpperCase(); keyError = validateKey(key); }}
                maxlength="20"
                placeholder={$t('project.keyPlaceholder')}
                class="w-32 text-sm px-3 py-2 border rounded-lg bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500 font-mono uppercase
                  {keyError ? 'border-red-400' : 'border-slate-200 dark:border-slate-600'}"
              />
              {#if keyError}
                <span class="text-xs text-red-500">{keyError}</span>
              {:else if key}
                <span class="text-xs text-slate-400 font-mono">{key.toUpperCase()}-1, {key.toUpperCase()}-2, …</span>
              {:else}
                <span class="text-xs text-slate-400">{$t('project.keyAutoPreview')}</span>
              {/if}
            </div>
          </div>

          <div class="flex items-center gap-2 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
            <span class="w-3 h-3 rounded-full" style="background-color: {color}"></span>
            <span class="text-sm font-medium text-slate-700 dark:text-slate-200">{name || $t('project.previewName')}</span>
            {#if key}
              <span class="ml-auto text-xs font-mono text-slate-400">{key.toUpperCase()}</span>
            {/if}
          </div>
        </div>
      </div>

      <div class="flex items-center justify-end gap-2 px-6 py-4 bg-slate-50 dark:bg-slate-800/50 border-t border-slate-100 dark:border-slate-700">
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
