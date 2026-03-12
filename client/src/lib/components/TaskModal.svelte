<script lang="ts">
  import { tasksApi } from '$lib/api/tasks';
  import type { TaskStatus, TaskPriority, User } from '$lib/types';
  import { TASK_STATUSES, PRIORITY_CONFIG } from '$lib/types';
  import AssigneePicker from './AssigneePicker.svelte';
  import { t } from '$lib/i18n';
  import { onMount } from 'svelte';

  const {
    projectId,
    defaultStatus = 'backlog',
    onClose,
    onCreated,
  }: {
    projectId: string;
    defaultStatus?: TaskStatus;
    onClose: () => void;
    onCreated: () => void;
  } = $props();

  let title = $state('');
  let description = $state('');
  let status = $state<TaskStatus>(defaultStatus);
  let priority = $state<TaskPriority>('medium');
  let assignee = $state<User | null>(null);
  let saving = $state(false);
  let titleEl = $state<HTMLInputElement | null>(null);

  onMount(() => titleEl?.focus());

  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    saving = true;
    try {
      await tasksApi.create(projectId, { title, description, status, priority, assignee_id: assignee?.id ?? null });
      onCreated();
    } finally {
      saving = false;
    }
  }
</script>

<svelte:window onkeydown={(e) => e.key === 'Escape' && onClose()} />

<div class="fixed inset-0 z-50 flex items-center justify-center">
  <div class="absolute inset-0 bg-black/30" onclick={onClose}></div>
  <div class="relative bg-white dark:bg-slate-900 rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden">
    <form onsubmit={handleSubmit}>
      <div class="p-6">
        <h2 class="text-base font-semibold text-slate-800 dark:text-slate-100 mb-4">{$t('task.new')}</h2>
        <div class="space-y-3">
          <input
            bind:this={titleEl}
            type="text"
            bind:value={title}
            placeholder={$t('task.titlePlaceholder')}
            class="w-full text-sm px-3 py-2.5 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
            required
          />
          <textarea
            bind:value={description}
            placeholder={$t('task.descriptionPlaceholder')}
            rows="3"
            class="w-full text-sm px-3 py-2.5 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent resize-none"
          ></textarea>
          <div>
            <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">{$t('task.assignee')}</label>
            <AssigneePicker value={assignee} onChange={(u) => (assignee = u)} />
          </div>
          <div class="flex gap-3">
            <div class="flex-1">
              <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">{$t('task.status')}</label>
              <select bind:value={status} class="w-full text-sm px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500">
                {#each TASK_STATUSES as s}
                  <option value={s.value}>{$t(`status.${s.value}` as any)}</option>
                {/each}
              </select>
            </div>
            <div class="flex-1">
              <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">{$t('task.priority')}</label>
              <select bind:value={priority} class="w-full text-sm px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500">
                {#each PRIORITY_CONFIG as p}
                  <option value={p.value}>{p.icon} {$t(`priority.${p.value}` as any)}</option>
                {/each}
              </select>
            </div>
          </div>
        </div>
      </div>
      <div class="flex items-center justify-end gap-2 px-6 py-4 bg-slate-50 dark:bg-slate-800/50 border-t border-slate-100 dark:border-slate-700">
        <button type="button" onclick={onClose} class="px-4 py-2 text-sm text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 transition-colors">
          {$t('common.cancel')}
        </button>
        <button
          type="submit"
          disabled={!title.trim() || saving}
          class="px-4 py-2 text-sm font-medium bg-brand-500 hover:bg-brand-600 text-white rounded-lg transition-colors disabled:opacity-50"
        >
          {saving ? $t('task.creating') : $t('task.create')}
        </button>
      </div>
    </form>
  </div>
</div>
