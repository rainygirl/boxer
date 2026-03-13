<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import type { Task, TaskPriority, User, ProjectMember } from '$lib/types';
  import { PRIORITY_CONFIG } from '$lib/types';
  import { tasksApi } from '$lib/api/tasks';
  import { matchKorean } from '$lib/utils/hangul';
  import { t, dateLocale } from '$lib/i18n';
  import DatePicker from './DatePicker.svelte';

  const { task, onUpdate }: { task: Task; onUpdate: () => void } = $props();

  const projectId = $derived(($page.params as any).projectId as string);
  let showPriorityMenu = $state(false);
  let showAssigneeMenu = $state(false);
  let assigneeQuery = $state('');
  let assigneeInputEl = $state<HTMLInputElement | null>(null);
  const members = $derived<ProjectMember[]>(
    (($page.data as any)?.projects ?? []).find((p: any) => p.id === projectId)?.members ?? []
  );

  // fixed 위치 계산용
  let priorityRect = $state<{ top: number; bottom: number; left: number } | null>(null);
  let assigneeRect = $state<{ top: number; bottom: number; right: number } | null>(null);

  const PRIORITY_POPUP_H = PRIORITY_CONFIG.length * 36 + 8; // ~188px
  const ASSIGNEE_POPUP_H = 260; // input + list max-h-44

  function popupTop(triggerTop: number, triggerBottom: number, popupH: number): number {
    const ideal = triggerTop - popupH - 4; // 위로 열기
    if (ideal >= 20) return ideal;
    return Math.min(triggerBottom + 4, window.innerHeight - popupH - 20); // 아래로 열기
  }

  const priority = $derived(PRIORITY_CONFIG.find((p) => p.value === task.priority));

  function formatCreatedAt(isoStr: string, locale: string): string {
    const d = new Date(isoStr);
    const now = new Date();
    const isToday = d.getFullYear() === now.getFullYear()
      && d.getMonth() === now.getMonth()
      && d.getDate() === now.getDate();
    if (isToday) return d.toLocaleTimeString(locale, { hour: '2-digit', minute: '2-digit' });
    return d.toLocaleDateString(locale, { month: 'short', day: 'numeric' });
  }

  const filteredMembers = $derived(
    assigneeQuery.trim()
      ? members.filter((m) =>
          matchKorean(assigneeQuery, m.user.name) ||
          m.user.email.toLowerCase().includes(assigneeQuery.toLowerCase())
        )
      : members
  );

  async function setPriority(p: TaskPriority, e: MouseEvent) {
    e.stopPropagation();
    showPriorityMenu = false;
    await tasksApi.update(task.id, { priority: p });
    onUpdate();
  }

  async function setAssignee(user: User | null) {
    showAssigneeMenu = false;
    assigneeQuery = '';
    await tasksApi.update(task.id, { assignee_id: user?.id ?? null });
    onUpdate();
  }

  function openPriorityMenu(e: MouseEvent) {
    e.stopPropagation();
    showAssigneeMenu = false;
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    priorityRect = { top: rect.top, bottom: rect.bottom, left: rect.left };
    showPriorityMenu = !showPriorityMenu;
  }

  function openAssigneeMenu(e: MouseEvent) {
    e.stopPropagation();
    showPriorityMenu = false;
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    assigneeRect = { top: rect.top, bottom: rect.bottom, right: window.innerWidth - rect.right };
    showAssigneeMenu = !showAssigneeMenu;
    if (showAssigneeMenu) setTimeout(() => assigneeInputEl?.focus(), 0);
  }

  function closeMenus() {
    setTimeout(() => {
      showPriorityMenu = false;
      showAssigneeMenu = false;
      assigneeQuery = '';
    }, 150);
  }
</script>

<svelte:window onclick={() => { showPriorityMenu = false; showAssigneeMenu = false; }} />

<div
  role="button"
  tabindex="0"
  onclick={() => goto(`/app/project/${task.project_id}/issue/${task.id}`)}
  onkeydown={(e) => e.key === 'Enter' && goto(`/app/project/${task.project_id}/issue/${task.id}`)}
  class="relative bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-3 cursor-pointer select-none hover:shadow-sm hover:border-slate-300 dark:hover:border-slate-600 transition-all"
>
  <div class="flex items-center gap-1.5 mb-1">
    <span class="text-[11px] font-mono font-medium text-slate-400 dark:text-slate-500">{task.ref}</span>
  </div>
  <p class="text-sm text-slate-700 dark:text-slate-200 font-medium leading-snug line-clamp-2 mb-2">
    {task.title}{#if task.subtasks?.length > 0}{@const done = task.subtasks.filter((s) => s.status === 'done').length}<span class="ml-1.5 text-[10px] font-medium px-1.5 py-0.5 rounded-full align-middle
      {done === task.subtasks.length
        ? 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400'
        : 'bg-slate-100 text-slate-500 dark:bg-slate-700 dark:text-slate-400'}"
    >{Math.round(done / task.subtasks.length * 100)}%</span>{/if}
  </p>

  <div class="flex items-center justify-between">
    <!-- Priority -->
    <button
      onclick={openPriorityMenu}
      class="flex items-center gap-1 rounded px-0.5 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
    >
      <span class="text-base leading-none">{priority?.icon}</span>
      <span class="text-[12px] text-slate-500 dark:text-slate-400 leading-none">{priority ? $t(`priority.${priority.value}` as any) : ''}</span>
    </button>

    <!-- Due date + Assignee -->
    <div class="flex items-center gap-1.5">
      <span onclick={(e) => e.stopPropagation()}>
        <DatePicker
          plain
          monthFormat="long"
          value={task.due_date ?? ''}
          placeholder={formatCreatedAt(task.created_at, $dateLocale)}
          onChange={async (v) => { await tasksApi.update(task.id, { due_date: v || null }); onUpdate(); }}
        />
      </span>

      <!-- Assignee -->
      <button
        onclick={openAssigneeMenu}
        class="rounded-full hover:ring-2 hover:ring-brand-400 hover:ring-offset-1 transition-all"
        title={task.assignee ? (task.assignee.name || task.assignee.email) : $t('assignee.assign')}
      >
        {#if task.assignee}
          {#if task.assignee.avatar_url}
            <img src={task.assignee.avatar_url} class="w-5 h-5 rounded-full" alt={task.assignee.name} />
          {:else}
            <div class="w-5 h-5 rounded-full bg-brand-400 text-white text-[10px] flex items-center justify-center font-medium">
              {task.assignee.name[0]}
            </div>
          {/if}
        {:else}
          <div class="w-5 h-5 rounded-full border border-dashed border-slate-300 dark:border-slate-600 flex items-center justify-center text-slate-300 dark:text-slate-600 text-[10px]">+</div>
        {/if}
      </button>
    </div>
  </div>
</div>

<!-- Priority 팝업 (fixed) -->
{#if showPriorityMenu && priorityRect}
  <div
    onclick={(e) => e.stopPropagation()}
    style="position: fixed; top: {popupTop(priorityRect.top, priorityRect.bottom, PRIORITY_POPUP_H)}px; left: {priorityRect.left}px;"
    class="z-[200] bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-xl shadow-lg overflow-hidden min-w-[130px]"
  >
    {#each PRIORITY_CONFIG as p}
      <button
        onmousedown={(e) => setPriority(p.value, e)}
        class="w-full flex items-center gap-2 px-3 py-2 text-sm transition-colors {task.priority === p.value ? 'bg-brand-50 dark:bg-brand-500/10 text-brand-600 dark:text-brand-400 font-medium' : 'text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700'}"
      >
        <span>{p.icon}</span>
        <span>{$t(`priority.${p.value}` as any)}</span>
      </button>
    {/each}
  </div>
{/if}

<!-- Assignee 팝업 (fixed) -->
{#if showAssigneeMenu && assigneeRect}
  <div
    onclick={(e) => e.stopPropagation()}
    style="position: fixed; top: {popupTop(assigneeRect.top, assigneeRect.bottom, ASSIGNEE_POPUP_H)}px; right: {assigneeRect.right}px;"
    class="z-[200] bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-xl shadow-lg overflow-hidden w-52"
  >
    <div class="p-2 border-b border-slate-100 dark:border-slate-700">
      <input
        bind:this={assigneeInputEl}
        bind:value={assigneeQuery}
        onblur={closeMenus}
        onclick={(e) => e.stopPropagation()}
        placeholder={$t('assignee.search')}
        class="w-full text-sm px-2 py-1 bg-slate-50 dark:bg-slate-700 text-slate-800 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 rounded-lg border-0 focus:outline-none focus:ring-2 focus:ring-brand-500"
      />
    </div>
    <ul class="max-h-44 overflow-y-auto scrollbar-thin py-1">
      <li>
        <button
          onmousedown={() => setAssignee(null)}
          class="w-full flex items-center gap-2 px-3 py-1.5 text-sm text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
        >
          <div class="w-5 h-5 rounded-full bg-slate-200 dark:bg-slate-600 flex items-center justify-center text-slate-400 text-[10px] shrink-0">-</div>
          <span>{$t('assignee.remove')}</span>
        </button>
      </li>
      {#each filteredMembers as m (m.user.id)}
        <li>
          <button
            onmousedown={() => setAssignee(m.user)}
            class="w-full flex items-center gap-2 px-3 py-1.5 text-sm hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors {task.assignee?.id === m.user.id ? 'bg-brand-50 dark:bg-brand-500/10' : ''}"
          >
            {#if m.user.avatar_url}
              <img src={m.user.avatar_url} class="w-5 h-5 rounded-full shrink-0" alt="" />
            {:else}
              <div class="w-5 h-5 rounded-full bg-brand-400 text-white text-[10px] flex items-center justify-center shrink-0">
                {(m.user.name || m.user.email)[0]}
              </div>
            {/if}
            <span class="text-slate-700 dark:text-slate-200 truncate">{m.user.name || m.user.email}</span>
          </button>
        </li>
      {/each}
      {#if filteredMembers.length === 0}
        <li class="px-3 py-2 text-sm text-slate-400 dark:text-slate-500 text-center">{$t('assignee.noResults')}</li>
      {/if}
    </ul>
  </div>
{/if}

