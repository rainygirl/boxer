<script lang="ts">
  import { tasksApi } from '$lib/api/tasks';
  import type { TaskStatus, TaskPriority, User } from '$lib/types';
  import { TASK_STATUSES, PRIORITY_CONFIG } from '$lib/types';
  import AssigneePicker from './AssigneePicker.svelte';
  import { t } from '$lib/i18n';
  import { onMount } from 'svelte';
  import { registerPopup, closeActivePopup, popupLeft } from '$lib/stores/popup';

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

  let statusOpen = $state(false);
  let priorityOpen = $state(false);
  let statusBtnEl = $state<HTMLElement | null>(null);
  let priorityBtnEl = $state<HTMLElement | null>(null);
  let statusPopupPos = $state({ top: 0, left: 0, width: 0 });
  let priorityPopupPos = $state({ top: 0, left: 0, width: 0 });

  onMount(() => titleEl?.focus());

  function openStatusDropdown(e: MouseEvent) {
    e.stopPropagation();
    if (statusOpen) { statusOpen = false; closeActivePopup(); return; }
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const popupH = TASK_STATUSES.length * 34 + 8;
    const top = rect.bottom + 4 + popupH > window.innerHeight ? rect.top - popupH - 4 : rect.bottom + 4;
    statusPopupPos = { top, left: popupLeft(rect.left, Math.max(rect.width, 150)), width: rect.width };
    statusOpen = true;
    priorityOpen = false;
    registerPopup(() => { statusOpen = false; });
  }

  function openPriorityDropdown(e: MouseEvent) {
    e.stopPropagation();
    if (priorityOpen) { priorityOpen = false; closeActivePopup(); return; }
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const popupH = PRIORITY_CONFIG.length * 34 + 8;
    const top = rect.bottom + 4 + popupH > window.innerHeight ? rect.top - popupH - 4 : rect.bottom + 4;
    priorityPopupPos = { top, left: popupLeft(rect.left, Math.max(rect.width, 160)), width: rect.width };
    priorityOpen = true;
    statusOpen = false;
    registerPopup(() => { priorityOpen = false; });
  }

  const statusCfg = $derived(TASK_STATUSES.find((s) => s.value === status)!);
  const priorityCfg = $derived(PRIORITY_CONFIG.find((p) => p.value === priority)!);

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

<svelte:window
  onkeydown={(e) => e.key === 'Escape' && onClose()}
  onclick={() => closeActivePopup()}
/>

<div class="fixed inset-0 z-50 flex items-center justify-center">
  <div class="absolute inset-0 bg-black/60" onclick={onClose}></div>
  <div class="relative bg-white dark:bg-slate-900 rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden">
    <form onsubmit={handleSubmit}>
      <div class="flex items-center justify-between px-6 pt-5 pb-0">
        <h2 class="text-base font-semibold text-slate-800 dark:text-slate-100">{$t('task.new')}</h2>
        <button type="button" onclick={onClose} class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 w-7 h-7 flex items-center justify-center rounded hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">✕</button>
      </div>
      <div class="p-6">
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
            <!-- Status -->
            <div class="flex-1">
              <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">{$t('task.status')}</label>
              <button
                type="button"
                bind:this={statusBtnEl}
                onclick={openStatusDropdown}
                class="w-full flex items-center gap-2 px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                <span class="inline-block px-2 py-0.5 rounded-full text-xs font-medium {statusCfg.color} {statusCfg.bg}">
                  {$t(`status.${status}` as any)}
                </span>
                <svg class="w-3 h-3 text-slate-400 ml-auto opacity-70" viewBox="0 0 10 6" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="1,1 5,5 9,1"/>
                </svg>
              </button>
            </div>

            <!-- Priority -->
            <div class="flex-1">
              <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">{$t('task.priority')}</label>
              <button
                type="button"
                bind:this={priorityBtnEl}
                onclick={openPriorityDropdown}
                class="w-full flex items-center gap-2 px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                <span class="text-base leading-none">{priorityCfg.icon}</span>
                <span class="text-slate-700 dark:text-slate-200">{$t(`priority.${priority}` as any)}</span>
                <svg class="w-3 h-3 text-slate-400 ml-auto opacity-70" viewBox="0 0 10 6" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="1,1 5,5 9,1"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
      <div class="flex items-center justify-end gap-2 px-6 py-4 bg-slate-50 dark:bg-slate-800/50 border-t border-slate-100 dark:border-slate-700">
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

{#if statusOpen}
  <div
    onclick={(e) => e.stopPropagation()}
    style="position: fixed; top: {statusPopupPos.top}px; left: {statusPopupPos.left}px; min-width: {statusPopupPos.width}px;"
    class="z-[200] bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-xl shadow-lg overflow-hidden py-1"
  >
    {#each TASK_STATUSES as s}
      <button
        type="button"
        onclick={() => { status = s.value; statusOpen = false; }}
        class="w-full flex items-center gap-2 px-3 py-2 text-xs transition-colors hover:bg-slate-50 dark:hover:bg-slate-700"
      >
        <span class="inline-block px-2 py-0.5 rounded-full font-medium {s.color} {s.bg}">
          {$t(`status.${s.value}` as any)}
        </span>
      </button>
    {/each}
  </div>
{/if}

{#if priorityOpen}
  <div
    onclick={(e) => e.stopPropagation()}
    style="position: fixed; top: {priorityPopupPos.top}px; left: {priorityPopupPos.left}px; min-width: {priorityPopupPos.width}px;"
    class="z-[200] bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-xl shadow-lg overflow-hidden py-1"
  >
    {#each PRIORITY_CONFIG as p}
      <button
        type="button"
        onclick={() => { priority = p.value; priorityOpen = false; }}
        class="w-full flex items-center gap-2 px-3 py-2 text-sm transition-colors hover:bg-slate-50 dark:hover:bg-slate-700"
      >
        <span class="text-base leading-none">{p.icon}</span>
        <span class="text-slate-700 dark:text-slate-200">{$t(`priority.${p.value}` as any)}</span>
      </button>
    {/each}
  </div>
{/if}
