<script lang="ts">
  import type { Task, TaskStatus, TaskPriority } from '$lib/types';
  import { TASK_STATUSES, PRIORITY_CONFIG } from '$lib/types';
  import { tasksApi } from '$lib/api/tasks';
  import { t, dateLocale } from '$lib/i18n';
  import TaskDetailPanel from './TaskDetailPanel.svelte';

  const {
    projectId,
    tasks,
    onUpdate,
  }: { projectId: string; tasks: Task[]; onUpdate: () => void } = $props();

  type SortKey = 'created_at' | 'priority' | 'status' | 'title';
  let sortKey = $state<SortKey>('created_at');
  let sortDir = $state<'asc' | 'desc'>('desc');
  let selectedTask = $state<Task | null>(null);

  const priorityOrder: Record<TaskPriority, number> = { urgent: 0, high: 1, medium: 2, low: 3, none: 4 };
  const statusOrder: Record<TaskStatus, number> = { backlog: 0, todo: 1, in_progress: 2, done: 3, confirmed: 4, cancelled: 5 };

  const sorted = $derived([...tasks].sort((a, b) => {
    let cmp = 0;
    if (sortKey === 'title') cmp = a.title.localeCompare(b.title);
    else if (sortKey === 'priority') cmp = priorityOrder[a.priority] - priorityOrder[b.priority];
    else if (sortKey === 'status') cmp = statusOrder[a.status] - statusOrder[b.status];
    else cmp = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
    return sortDir === 'asc' ? cmp : -cmp;
  }));

  function toggleSort(key: SortKey) {
    if (sortKey === key) sortDir = sortDir === 'asc' ? 'desc' : 'asc';
    else { sortKey = key; sortDir = 'asc'; }
  }

  async function updateTask(id: string, data: Parameters<typeof tasksApi.update>[1]) {
    await tasksApi.update(id, data);
    onUpdate();
  }

  async function deleteTask(task: Task) {
    if (!confirm($t('task.deleteConfirm'))) return;
    await tasksApi.delete(task.id);
    onUpdate();
  }

  function sortIcon(key: SortKey) {
    return sortKey === key ? (sortDir === 'asc' ? '↑' : '↓') : '';
  }
</script>

<div class="h-full overflow-auto scrollbar-thin bg-white dark:bg-slate-900">
  <table class="w-full text-sm border-collapse">
    <thead class="sticky top-0 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700 z-10">
      <tr>
        {#each ([['title', $t('table.task')], ['status', $t('table.status')], ['priority', $t('table.priority')], ['created_at', $t('table.createdAt')]] as const) as [key, label]}
          <th
            class="text-left px-4 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 cursor-pointer select-none hover:text-slate-700 dark:hover:text-slate-200"
            onclick={() => toggleSort(key as SortKey)}
          >
            {label} {sortIcon(key as SortKey)}
          </th>
        {/each}
        <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 w-32">{$t('table.assignee')}</th>
        <th class="w-10"></th>
      </tr>
    </thead>
    <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
      {#each sorted as task (task.id)}
        {@const statusCfg = TASK_STATUSES.find((s) => s.value === task.status)!}
        {@const priorityCfg = PRIORITY_CONFIG.find((p) => p.value === task.priority)!}
        <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50 group transition-colors">
          <!-- Title -->
          <td class="px-4 py-3">
            <button
              class="text-left font-medium text-slate-700 dark:text-slate-200 hover:text-brand-600 dark:hover:text-brand-400 transition-colors line-clamp-1"
              onclick={() => (selectedTask = task)}
            >{task.title}</button>
          </td>

          <!-- Status -->
          <td class="px-4 py-3">
            <select
              value={task.status}
              onchange={(e) => updateTask(task.id, { status: e.currentTarget.value as TaskStatus })}
              class="text-xs font-medium px-2 py-1 rounded-full border-0 cursor-pointer {statusCfg.color} {statusCfg.bg}"
            >
              {#each TASK_STATUSES as s}
                <option value={s.value}>{$t(`status.${s.value}` as any)}</option>
              {/each}
            </select>
          </td>

          <!-- Priority -->
          <td class="px-4 py-3">
            <select
              value={task.priority}
              onchange={(e) => updateTask(task.id, { priority: e.currentTarget.value as TaskPriority })}
              class="text-xs bg-transparent dark:text-slate-300 border-0 cursor-pointer"
            >
              {#each PRIORITY_CONFIG as p}
                <option value={p.value}>{p.icon} {$t(`priority.${p.value}` as any)}</option>
              {/each}
            </select>
          </td>

          <!-- Created at -->
          <td class="px-4 py-3 text-xs text-slate-400 dark:text-slate-500">
            {new Date(task.created_at).toLocaleDateString($dateLocale, { month: 'short', day: 'numeric' })}
          </td>

          <!-- Assignee -->
          <td class="px-4 py-3">
            {#if task.assignee}
              <div class="flex items-center gap-1.5">
                {#if task.assignee.avatar_url}
                  <img src={task.assignee.avatar_url} class="w-5 h-5 rounded-full" alt="" />
                {:else}
                  <div class="w-5 h-5 rounded-full bg-brand-400 text-white text-[10px] flex items-center justify-center">
                    {task.assignee.name[0]}
                  </div>
                {/if}
                <span class="text-xs text-slate-600 dark:text-slate-400 truncate max-w-[80px]">{task.assignee.name}</span>
              </div>
            {:else}
              <span class="text-xs text-slate-300 dark:text-slate-600">-</span>
            {/if}
          </td>

          <!-- Delete -->
          <td class="px-2 py-3">
            <button
              onclick={() => deleteTask(task)}
              class="opacity-0 group-hover:opacity-100 text-slate-300 dark:text-slate-600 hover:text-red-400 transition-all text-xs w-6 h-6 flex items-center justify-center"
            >✕</button>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>

  {#if tasks.length === 0}
    <div class="flex flex-col items-center justify-center py-20 text-slate-400 dark:text-slate-600">
      <p class="text-sm">{$t('task.noTasks')}</p>
    </div>
  {/if}
</div>

{#if selectedTask}
  <TaskDetailPanel
    task={selectedTask}
    onClose={() => (selectedTask = null)}
    onUpdate={() => { selectedTask = null; onUpdate(); }}
  />
{/if}
