<script lang="ts">
  import { get } from 'svelte/store';
  import { TASK_STATUSES, type Task, type TaskStatus, type Project } from '$lib/types';
  import { tasksApi } from '$lib/api/tasks';
  import { projectsApi } from '$lib/api/projects';
  import { sidebarHoverProjectId } from '$lib/stores/drag';
  import { toastStore } from '$lib/stores/toast';
  import KanbanColumn from './KanbanColumn.svelte';

  const {
    project,
    projects = [],
    tasks,
    onUpdate,
  }: { project: Project; projects?: Project[]; tasks: Task[]; onUpdate: () => void } = $props();

  type ColumnMap = Record<TaskStatus, (Task & { id: string })[]>;

  const makeColumns = (taskList: Task[]): ColumnMap => {
    const map = Object.fromEntries(
      TASK_STATUSES.map((s) => [s.value, [] as Task[]])
    ) as unknown as ColumnMap;
    for (const t of taskList) map[t.status].push(t);
    return map;
  };

  let columns = $state<ColumnMap>(makeColumns(tasks));
  let showColumnSettings = $state(false);
  let savingColumns = $state(false);
  let localDisabled = $state<TaskStatus[]>([...(project.disabled_statuses ?? [])]);

  $effect(() => {
    columns = makeColumns(tasks);
  });

  const activeStatuses = $derived(
    TASK_STATUSES.filter((s) => !localDisabled.includes(s.value))
  );

  async function toggleColumn(status: TaskStatus) {
    const isDisabled = localDisabled.includes(status);
    localDisabled = isDisabled
      ? localDisabled.filter((s) => s !== status)
      : [...localDisabled, status];

    if (localDisabled.length >= TASK_STATUSES.length) {
      localDisabled = localDisabled.filter((s) => s !== status);
      return;
    }

    savingColumns = true;
    try {
      await projectsApi.updateColumns(project.id, localDisabled);
    } catch {
      localDisabled = [...(project.disabled_statuses ?? [])];
    } finally {
      savingColumns = false;
    }
  }

  async function handleMove(taskId: string, toStatus: TaskStatus, newItems: Task[]) {
    const above = newItems[newItems.findIndex((t) => t.id === taskId) - 1];
    const below = newItems[newItems.findIndex((t) => t.id === taskId) + 1];
    const sort_order =
      above && below
        ? (above.sort_order + below.sort_order) / 2
        : above
          ? above.sort_order + 1000
          : below
            ? below.sort_order - 1000
            : 1000;

    try {
      await tasksApi.move(taskId, toStatus, sort_order);
      onUpdate();
    } catch {
      columns = makeColumns(tasks);
    }
  }

  async function handleDroppedOutside(task: Task) {
    const targetProjectId = get(sidebarHoverProjectId);
    sidebarHoverProjectId.set(null);

    // Not hovering over a sidebar project — revert
    if (!targetProjectId || targetProjectId === project.id) {
      columns = makeColumns(tasks);
      return;
    }

    const targetProject = projects.find((p) => p.id === targetProjectId);
    if (!targetProject) {
      columns = makeColumns(tasks);
      return;
    }

    const isStatusActive = !targetProject.disabled_statuses?.includes(task.status);
    const firstActive = TASK_STATUSES.find(
      (s) => !targetProject.disabled_statuses?.includes(s.value)
    );
    const finalStatus = isStatusActive ? task.status : (firstActive?.value ?? 'backlog');

    try {
      await tasksApi.move(task.id, finalStatus, Date.now(), targetProjectId);
      onUpdate();

      const statusLabel = TASK_STATUSES.find((s) => s.value === finalStatus)?.label ?? finalStatus;
      if (!isStatusActive) {
        toastStore.add(
          `"${task.title}" → ${targetProject.name} / ${statusLabel} (카테고리 비활성으로 이동됨)`,
          'info'
        );
      } else {
        toastStore.add(`"${task.title}" → ${targetProject.name} / ${statusLabel}`, 'success');
      }
    } catch {
      toastStore.add('태스크 이동에 실패했습니다.', 'error');
      columns = makeColumns(tasks);
    }
  }

  function handleColumnUpdate(status: TaskStatus, newItems: (Task & { id: string })[]) {
    columns = { ...columns, [status]: newItems };
  }
</script>

<div class="flex flex-col h-full bg-slate-50 dark:bg-slate-950">
  <!-- Column settings bar -->
  <div class="flex items-center justify-end px-4 pt-2 pb-0 gap-2">
    <div class="relative">
      <button
        onclick={() => (showColumnSettings = !showColumnSettings)}
        class="flex items-center gap-1.5 text-xs text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300 px-2 py-1 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-800 transition-colors"
        title="컬럼 설정"
      >
        <svg class="w-3.5 h-3.5" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M6.5 1h3M8 1v2M3 5h10M4 8h8M5.5 11h5M7 14h2" stroke-linecap="round"/>
        </svg>
        <span>컬럼</span>
        {#if localDisabled.length > 0}
          <span class="bg-brand-500 text-white text-[10px] rounded-full w-4 h-4 flex items-center justify-center font-medium">{localDisabled.length}</span>
        {/if}
      </button>

      {#if showColumnSettings}
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div
          class="absolute right-0 top-full mt-1 z-50 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-lg py-2 min-w-[160px]"
          onmouseleave={() => (showColumnSettings = false)}
        >
          <p class="text-[11px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider px-3 pb-1">표시할 컬럼</p>
          {#each TASK_STATUSES as s}
            {@const isDisabled = localDisabled.includes(s.value)}
            <button
              onclick={() => toggleColumn(s.value)}
              disabled={savingColumns}
              class="w-full flex items-center gap-2 px-3 py-1.5 text-sm hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors disabled:opacity-50"
            >
              <span class="w-4 h-4 rounded border-2 flex items-center justify-center shrink-0
                {isDisabled ? 'border-slate-300 dark:border-slate-600' : 'border-brand-500 bg-brand-500'}">
                {#if !isDisabled}
                  <svg class="w-2.5 h-2.5 text-white" viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1.5 5l2.5 3 4.5-6" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                {/if}
              </span>
              <span class="text-xs font-medium px-1.5 py-0.5 rounded-full {s.color} {s.bg}">{s.label}</span>
            </button>
          {/each}
        </div>
      {/if}
    </div>
  </div>

  <!-- Board -->
  <div class="flex gap-3 flex-1 overflow-x-auto p-4 pt-2 scrollbar-thin">
    {#each activeStatuses as col (col.value)}
      <KanbanColumn
        projectId={project.id}
        status={col}
        tasks={columns[col.value]}
        allColumns={columns}
        onUpdate={handleColumnUpdate}
        onMove={handleMove}
        onTaskCreated={onUpdate}
        onDroppedOutside={handleDroppedOutside}
      />
    {/each}
  </div>
</div>
