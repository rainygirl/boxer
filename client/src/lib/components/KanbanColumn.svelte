<script lang="ts">
  import { dndzone, TRIGGERS, type DndEvent } from 'svelte-dnd-action';
  import { get } from 'svelte/store';
  import { flip } from 'svelte/animate';
  import type { Task, TaskStatus } from '$lib/types';
  import { t } from '$lib/i18n';
  import { draggingTask } from '$lib/stores/drag';
  import TaskCard from './TaskCard.svelte';
  import TaskModal from './TaskModal.svelte';

  type ColConfig = { value: TaskStatus; label: string; color: string; bg: string };
  type ColumnMap = Record<TaskStatus, Task[]>;

  const {
    projectId,
    status,
    tasks,
    allColumns,
    onUpdate,
    onMove,
    onTaskCreated,
    onDroppedOutside,
  }: {
    projectId: string;
    status: ColConfig;
    tasks: Task[];
    allColumns: ColumnMap;
    onUpdate: (status: TaskStatus, items: Task[]) => void;
    onMove: (taskId: string, toStatus: TaskStatus, newItems: Task[]) => void;
    onTaskCreated: () => void;
    onDroppedOutside: (task: Task) => void;
  } = $props();

  let showCreate = $state(false);
  const FLIP_MS = 150;

  const isDragOver = $derived(tasks.some((t: any) => t.isDndShadowItem));

  function handleConsider(e: CustomEvent<DndEvent<Task>>) {
    const { items, info } = e.detail;
    // On drag start, record which task is being dragged
    if (info.trigger === TRIGGERS.DRAG_STARTED) {
      const task = tasks.find((t) => t.id === info.id);
      if (task) draggingTask.set(task);
    }
    onUpdate(status.value, items);
  }

  function handleFinalize(e: CustomEvent<DndEvent<Task>>) {
    // Read dragging task before clearing
    const task = get(draggingTask);
    draggingTask.set(null);

    const newItems = e.detail.items;
    const taskId = e.detail.info.id as string;
    const trigger = e.detail.info.trigger;

    onUpdate(status.value, newItems);

    // Dropped outside all zones (e.g. on sidebar) — delegate to parent
    if (trigger === TRIGGERS.DROPPED_OUTSIDE_OF_ANY) {
      if (task) onDroppedOutside(task);
      return;
    }

    // Item was dragged OUT of this column — target column handles the API call
    if (!newItems.some((t) => t.id === taskId)) return;

    // Item arrived from another column
    for (const t of newItems) {
      if (t.status !== status.value) {
        onMove(t.id, status.value, newItems);
        return;
      }
    }
    // Same-column reorder
    onMove(taskId, status.value, newItems);
  }
</script>

<div class="flex flex-col w-72 shrink-0">
  <!-- Column header -->
  <div class="flex items-center justify-between mb-2 px-1">
    <div class="flex items-center gap-2">
      <span class="text-xs font-semibold px-2 py-0.5 rounded-full {status.color} {status.bg}">
        {$t(`status.${status.value}` as any)}
      </span>
      <span class="text-xs text-slate-400 dark:text-slate-500 font-medium">{tasks.length}</span>
    </div>
    <button
      onclick={() => (showCreate = true)}
      class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 w-6 h-6 flex items-center justify-center rounded hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
      title={$t('task.addToStatus', { status: $t(`status.${status.value}` as any) })}
    >+</button>
  </div>

  <!-- Drop zone -->
  <div
    class="flex-1 rounded-xl p-2 min-h-[120px] transition-all {isDragOver
      ? 'bg-brand-100/50 dark:bg-brand-500/10 ring-2 ring-inset ring-brand-400 dark:ring-brand-500'
      : 'bg-slate-200/60 dark:bg-slate-800/60'}"
    use:dndzone={{
      items: tasks,
      flipDurationMs: FLIP_MS,
      type: 'task',
      dropTargetStyle: {},
      transformDraggedElement: (el: HTMLElement | undefined) => {
        if (!el) return;
        if (!el.dataset.frozenWidth) {
          el.dataset.frozenWidth = String(el.offsetWidth);
        }
        el.style.width = el.dataset.frozenWidth + 'px';
        el.style.maxWidth = el.dataset.frozenWidth + 'px';
        el.style.boxSizing = 'border-box';
      },
    }}
    onconsider={(e: CustomEvent) => handleConsider(e)}
    onfinalize={(e: CustomEvent) => handleFinalize(e)}
  >
    {#each tasks as task (task.id)}
      <div animate:flip={{ duration: FLIP_MS }} class="mb-2">
        {#if (task as any).isDndShadowItem}
          <div class="h-16 rounded-lg border-2 border-dashed border-brand-400/60 dark:border-brand-400/40"></div>
        {:else}
          <TaskCard {task} onUpdate={onTaskCreated} />
        {/if}
      </div>
    {/each}

    {#if tasks.length === 0}
      <div class="flex items-center justify-center h-16 text-slate-300 dark:text-slate-600 text-sm pointer-events-none">
        {$t('task.dragToMove')}
      </div>
    {/if}
  </div>
</div>

{#if showCreate}
  <TaskModal
    {projectId}
    defaultStatus={status.value}
    onClose={() => (showCreate = false)}
    onCreated={() => { showCreate = false; onTaskCreated(); }}
  />
{/if}
