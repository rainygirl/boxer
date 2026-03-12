<script lang="ts">
  import { TASK_STATUSES, type Task, type TaskStatus } from '$lib/types';
  import { tasksApi } from '$lib/api/tasks';
  import KanbanColumn from './KanbanColumn.svelte';

  const {
    projectId,
    tasks,
    onUpdate,
  }: { projectId: string; tasks: Task[]; onUpdate: () => void } = $props();

  // Local column state for optimistic DnD updates
  type ColumnMap = Record<TaskStatus, (Task & { id: string })[]>;

  const makeColumns = (taskList: Task[]): ColumnMap => {
    const map = Object.fromEntries(
      TASK_STATUSES.map((s) => [s.value, []])
    ) as ColumnMap;
    for (const t of taskList) map[t.status].push(t);
    return map;
  };

  let columns = $state<ColumnMap>(makeColumns(tasks));

  $effect(() => {
    columns = makeColumns(tasks);
  });

  async function handleMove(
    taskId: string,
    toStatus: TaskStatus,
    newItems: Task[]
  ) {
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
      // revert on error
      columns = makeColumns(tasks);
    }
  }

  function handleColumnUpdate(status: TaskStatus, newItems: (Task & { id: string })[]) {
    columns = { ...columns, [status]: newItems };
  }
</script>

<div class="flex gap-3 h-full overflow-x-auto p-4 scrollbar-thin bg-slate-50 dark:bg-slate-950">
  {#each TASK_STATUSES as col (col.value)}
    <KanbanColumn
      {projectId}
      status={col}
      tasks={columns[col.value]}
      allColumns={columns}
      onUpdate={handleColumnUpdate}
      onMove={handleMove}
      onTaskCreated={onUpdate}
    />
  {/each}
</div>
