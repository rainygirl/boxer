<script lang="ts">
  import { invalidate, goto } from '$app/navigation';
  import { projectsApi } from '$lib/api/projects';
  import type { Project } from '$lib/types';
  import { t } from '$lib/i18n';
  import { get } from 'svelte/store';
  import GitHubSettingsPanel from './GitHubSettingsPanel.svelte';
  import WebhooksPanel from './WebhooksPanel.svelte';

  const { project, onClose, onOpenMembers }: { project: Project; onClose: () => void; onOpenMembers: () => void } = $props();

  type Tab = 'general' | 'github' | 'webhooks';
  let activeTab = $state<Tab>('general');

  // General tab state
  let name = $state(project.name);
  let key = $state(project.key);
  let visibility = $state(project.visibility ?? 'private');
  let keyError = $state('');
  let nameError = $state('');
  let saving = $state(false);
  let saved = $state(false);
  let deleting = $state(false);
  let nameInputEl = $state<HTMLInputElement | null>(null);

  $effect(() => {
    if (activeTab === 'general') setTimeout(() => nameInputEl?.focus(), 0);
  });

  function validateKey(v: string): string {
    if (!v) return $t('project.keyRequired');
    if (!/^[A-Z]{1,5}$/.test(v)) return $t('project.keyFormat');
    return '';
  }

  function onKeyInput() {
    key = key.toUpperCase().replace(/[^A-Z]/g, '').slice(0, 5);
    keyError = validateKey(key);
    saved = false;
  }

  function onNameInput() {
    nameError = name.trim() ? '' : $t('project.nameRequired');
    saved = false;
  }

  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    nameError = name.trim() ? '' : $t('project.nameRequired');
    keyError = validateKey(key);
    if (nameError || keyError) return;

    const unchanged = name.trim() === project.name && key === project.key && visibility === project.visibility;
    if (unchanged) { onClose(); return; }

    saving = true;
    try {
      await projectsApi.update(project.id, { name: name.trim(), key, visibility });
      await invalidate('app:projects');
      saved = true;
      setTimeout(onClose, 600);
    } catch (err: any) {
      const detail = err?.response?.data?.detail ?? $t('project.saveFailed');
      if (typeof detail === 'string' && detail.toLowerCase().includes('key')) {
        keyError = detail;
      } else {
        nameError = detail;
      }
    } finally {
      saving = false;
    }
  }

  async function handleDelete() {
    if (!confirm(get(t)('project.deleteConfirm', { name: project.name }))) return;
    deleting = true;
    try {
      await projectsApi.delete(project.id);
      await invalidate('app:projects');
      onClose();
      goto('/app');
    } finally {
      deleting = false;
    }
  }
</script>

<svelte:window onkeydown={(e) => e.key === 'Escape' && onClose()} />

<div class="fixed inset-0 z-50 flex items-center justify-center">
  <div class="absolute inset-0 bg-black/60" onclick={onClose}></div>
  <div class="relative bg-white dark:bg-slate-900 rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden">
    <!-- Header -->
    <div class="flex items-center justify-between px-6 pt-5 pb-0">
      <h2 class="text-base font-semibold text-slate-800 dark:text-slate-100">{$t('project.settingsTitle')}</h2>
      <button type="button" onclick={onClose} class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 w-7 h-7 flex items-center justify-center rounded hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">✕</button>
    </div>

    <!-- Tabs -->
    <div class="flex gap-0 px-6 mt-4 border-b border-slate-100 dark:border-slate-700">
      {#each ([['general', $t('project.tabGeneral')], ['github', 'GitHub'], ['webhooks', $t('integration.tabWebhooks')]] as const) as [id, label]}
        <button
          type="button"
          onclick={() => (activeTab = id)}
          class="px-3 py-2 text-sm font-medium border-b-2 transition-colors -mb-px
                 {activeTab === id
                   ? 'border-brand-500 text-brand-600 dark:text-brand-400'
                   : 'border-transparent text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'}"
        >{label}</button>
      {/each}
    </div>

    <!-- Tab content -->
    <div class="p-6">

      {#if activeTab === 'general'}
        <form onsubmit={handleSubmit} class="space-y-4">
          <!-- 프로젝트명 -->
          <div>
            <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1.5">
              {$t('project.nameLabel')}
            </label>
            <input
              bind:this={nameInputEl}
              type="text"
              bind:value={name}
              oninput={onNameInput}
              placeholder={$t('project.namePlaceholder')}
              class="w-full text-sm px-3 py-2 border rounded-lg bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100
                     placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500
                     {nameError ? 'border-red-400' : 'border-slate-200 dark:border-slate-600'}"
            />
            {#if nameError}
              <p class="mt-1 text-xs text-red-500">{nameError}</p>
            {/if}
          </div>

          <!-- 프로젝트 키 -->
          <div>
            <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1.5">
              {$t('project.keyLabel')} <span class="font-normal text-slate-400">{$t('project.keyHint')}</span>
            </label>
            <div class="flex items-center gap-3">
              <input
                type="text"
                bind:value={key}
                oninput={onKeyInput}
                maxlength="5"
                placeholder={$t('project.keyPlaceholder')}
                class="w-28 text-sm px-3 py-2 border rounded-lg bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100
                       placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500 font-mono uppercase tracking-widest
                       {keyError ? 'border-red-400' : 'border-slate-200 dark:border-slate-600'}"
              />
              <span class="text-xs text-slate-400 font-mono">{key || '??'}-1, {key || '??'}-2 …</span>
            </div>
            {#if keyError}
              <p class="mt-1 text-xs text-red-500">{keyError}</p>
            {/if}
          </div>

          <!-- 공개 범위 -->
          <div>
            <p class="text-xs font-medium text-slate-500 dark:text-slate-400 mb-2">{$t('project.visibility')}</p>
            <div class="grid grid-cols-2 gap-2">
              {#each (['public', 'private'] as const) as v}
                <button
                  type="button"
                  onclick={() => { visibility = v; saved = false; }}
                  class="flex items-start gap-2.5 p-3 rounded-lg border text-left transition-colors
                         {visibility === v
                           ? 'border-brand-500 bg-brand-50 dark:bg-brand-500/20 dark:border-brand-400'
                           : 'border-slate-200 dark:border-slate-600 hover:border-slate-300 dark:hover:border-slate-500'}"
                >
                  <span class="mt-0.5 text-base leading-none">{v === 'public' ? '🌐' : '🔒'}</span>
                  <span>
                    <span class="block text-xs font-semibold text-slate-700 dark:text-slate-200">
                      {$t(v === 'public' ? 'project.visibilityPublic' : 'project.visibilityPrivate')}
                    </span>
                    <span class="block text-[11px] text-slate-400 dark:text-slate-500 mt-0.5">
                      {$t(v === 'public' ? 'project.visibilityPublicDesc' : 'project.visibilityPrivateDesc')}
                    </span>
                  </span>
                </button>
              {/each}
            </div>
          </div>

          <div class="flex items-center justify-between pt-2">
            <button
              type="button"
              onclick={() => { onClose(); onOpenMembers(); }}
              class="text-[12px] text-slate-400 dark:text-slate-500 hover:text-brand-500 dark:hover:text-brand-400 underline underline-offset-2 transition-colors"
            >{$t('project.manageMembers')}</button>
            <div class="flex items-center gap-3">
              <button
                type="button"
                onclick={handleDelete}
                disabled={deleting}
                class="text-[12px] text-red-400 hover:text-red-600 dark:text-red-500 dark:hover:text-red-400 underline underline-offset-2 transition-colors disabled:opacity-50"
              >{deleting ? '...' : $t('project.delete')}</button>
              <button
                type="submit"
                disabled={!!keyError || !!nameError || saving || saved}
                class="px-4 py-2 text-sm font-medium rounded-lg transition-colors
                       {saved ? 'bg-green-500 text-white' : 'bg-brand-500 hover:bg-brand-600 text-white disabled:opacity-50'}"
              >
                {saved ? $t('common.saved') : saving ? $t('common.saving') : $t('common.save')}
              </button>
            </div>
          </div>
        </form>

      {:else if activeTab === 'github'}
        <GitHubSettingsPanel projectId={project.id} />

      {:else if activeTab === 'webhooks'}
        <WebhooksPanel projectId={project.id} />
      {/if}

    </div>
  </div>
</div>
