<script lang="ts">
  import { dndzone, TRIGGERS } from 'svelte-dnd-action';
  import { goto } from '$app/navigation';
  import { get } from 'svelte/store';
  import { flip } from 'svelte/animate';
  import type { Task, TaskStatus, TaskPriority, Project, SubTask } from '$lib/types';
  import { TASK_STATUSES, PRIORITY_CONFIG } from '$lib/types';
  import { tasksApi } from '$lib/api/tasks';
  import { draggingTask, sidebarHoverProjectId } from '$lib/stores/drag';
  import { toastStore } from '$lib/stores/toast';
  import { t, dateLocale } from '$lib/i18n';
  import { registerPopup, closeActivePopup, popupLeft } from '$lib/stores/popup';
  import DatePicker from './DatePicker.svelte';
  import { matchKorean } from '$lib/utils/hangul';
  import type { User, ProjectMember } from '$lib/types';

  const {
    project,
    projects = [],
    tasks,
    onUpdate,
  }: { project: Project; projects?: Project[]; tasks: Task[]; onUpdate: () => void } = $props();

  // ── Sort ─────────────────────────────────────────────────────────────────
  type SortKey = 'title' | 'priority' | 'created_at';

  const STORAGE_KEY = `boxer:table-sort:${project.id}`;
  const COLLAPSE_KEY = `boxer:table-collapse:${project.id}`;

  function loadCollapsed(): Set<string> {
    try {
      const raw = localStorage.getItem(COLLAPSE_KEY);
      if (raw) return new Set(JSON.parse(raw));
    } catch {}
    return new Set();
  }

  function saveCollapsed(set: Set<string>) {
    try { localStorage.setItem(COLLAPSE_KEY, JSON.stringify([...set])); } catch {}
  }

  let collapsed = $state<Set<string>>(loadCollapsed());

  function toggleCollapse(status: string) {
    const next = new Set(collapsed);
    if (next.has(status)) next.delete(status);
    else next.add(status);
    collapsed = next;
    saveCollapsed(next);
  }

  function loadSort(): { key: SortKey | null; dir: 'asc' | 'desc' } {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) return JSON.parse(raw);
    } catch {}
    return { key: null, dir: 'asc' };
  }

  function saveSort(key: SortKey | null, dir: 'asc' | 'desc') {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify({ key, dir })); } catch {}
  }

  const initial = loadSort();
  let sortKey = $state<SortKey | null>(initial.key);
  let sortDir = $state<'asc' | 'desc'>(initial.dir);

  const priorityOrder: Record<TaskPriority, number> = { urgent: 0, high: 1, medium: 2, low: 3, none: 4 };

  function applySortKey(list: Task[], key: SortKey | null, dir: 'asc' | 'desc') {
    const arr = [...list];
    if (key === null) return arr.sort((a, b) => a.sort_order - b.sort_order);
    arr.sort((a, b) => {
      let cmp = 0;
      if (key === 'title')      cmp = a.title.localeCompare(b.title);
      else if (key === 'priority') cmp = priorityOrder[a.priority] - priorityOrder[b.priority];
      else cmp = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
      return dir === 'asc' ? cmp : -cmp;
    });
    return arr;
  }

  // ── Groups (by status) ───────────────────────────────────────────────────
  type GroupMap = Record<string, (Task & { id: string })[]>;

  function buildGroups(sorted: Task[]): GroupMap {
    const result: GroupMap = {};
    for (const s of TASK_STATUSES) {
      result[s.value] = sorted.filter((t) => t.status === s.value) as any;
    }
    return result;
  }

  let groups = $state<GroupMap>(buildGroups(applySortKey(tasks, initial.key, initial.dir)));

  $effect(() => {
    groups = buildGroups(applySortKey(tasks, sortKey, sortDir));
  });

  // ── Subtasks ─────────────────────────────────────────────────────────────
  // subtaskOverrides: optimistic local state for toggled subtasks until onUpdate() refreshes tasks
  let subtaskOverrides = $state<Record<string, SubTask[]>>({});

  function getSubtasks(task: Task): SubTask[] {
    return subtaskOverrides[task.id] ?? task.subtasks ?? [];
  }

  async function toggleSubtaskInTable(task: Task, sub: SubTask) {
    const updated = await tasksApi.updateSubtask(task.id, sub.id, { is_done: sub.status !== 'done' });
    subtaskOverrides = {
      ...subtaskOverrides,
      [task.id]: getSubtasks(task).map((s) => (s.id === sub.id ? updated : s)),
    };
  }

  function toggleSort(key: SortKey) {
    if (sortKey === key) sortDir = sortDir === 'asc' ? 'desc' : 'asc';
    else { sortKey = key; sortDir = 'asc'; }
    saveSort(sortKey, sortDir);
    groups = buildGroups(applySortKey(tasks, sortKey, sortDir));
  }

  function sortIcon(key: SortKey) {
    if (sortKey !== key) return '';
    return sortDir === 'asc' ? ' ↑' : ' ↓';
  }

  // ── Header / sidebar drop targets (pointer-based) ────────────────────────
  let headerDragOver = $state<string | null>(null);
  // Flag set when onUp handles a sidebar drop, so handleFinalize skips its logic
  let sidebarDropHandled = false;

  $effect(() => {
    function onMove(e: PointerEvent) {
      if (!get(draggingTask)) { headerDragOver = null; return; }
      const els = document.elementsFromPoint(e.clientX, e.clientY) as HTMLElement[];
      const header = els.find(el => el.dataset.statusHeader);
      headerDragOver = header?.dataset.statusHeader ?? null;
    }

    function onUp() {
      const task = get(draggingTask);
      const hoverProjectId = get(sidebarHoverProjectId);
      const h = headerDragOver;
      headerDragOver = null;

      if (!task) return;

      // Header drop: change status within the same project
      if (h && task.status !== h) {
        tasksApi.move(task.id, h as TaskStatus, task.sort_order)
          .then(() => onUpdate())
          .catch(() => toastStore.add('이슈 이동에 실패했습니다.', 'error'));
        return;
      }

      // Sidebar project drop: move to a different project.
      // Table rows span full width so DROPPED_OUTSIDE_OF_ANY never fires —
      // detect this via sidebarHoverProjectId instead.
      if (hoverProjectId && hoverProjectId !== project.id) {
        sidebarDropHandled = true;
        sidebarHoverProjectId.set(null);
        draggingTask.set(null);
        handleDroppedOutside(task, hoverProjectId);
      }
    }

    document.addEventListener('pointermove', onMove, { passive: true });
    document.addEventListener('pointerup', onUp);
    return () => {
      document.removeEventListener('pointermove', onMove);
      document.removeEventListener('pointerup', onUp);
    };
  });

  // ── Status popup ─────────────────────────────────────────────────────────
  let statusPopup = $state<{ taskId: string; top: number; left: number } | null>(null);

  function openStatusPopup(e: MouseEvent, taskId: string) {
    e.stopPropagation();
    if (statusPopup?.taskId === taskId) { statusPopup = null; closeActivePopup(); return; }
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const popupH = TASK_STATUSES.length * 34 + 8;
    const top = rect.bottom + 4 + popupH > window.innerHeight ? rect.top - popupH - 4 : rect.bottom + 4;
    statusPopup = { taskId, top, left: popupLeft(rect.left, 150) };
    priorityPopup = null;
    registerPopup(() => { statusPopup = null; });
  }

  async function setStatus(taskId: string, status: TaskStatus) {
    statusPopup = null;
    await updateTask(taskId, { status });
  }

  // ── Priority popup ────────────────────────────────────────────────────────
  let priorityPopup = $state<{ taskId: string; top: number; left: number } | null>(null);

  function openPriorityPopup(e: MouseEvent, taskId: string) {
    e.stopPropagation();
    if (priorityPopup?.taskId === taskId) { priorityPopup = null; closeActivePopup(); return; }
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const popupH = PRIORITY_CONFIG.length * 34 + 8;
    const top = rect.bottom + 4 + popupH > window.innerHeight ? rect.top - popupH - 4 : rect.bottom + 4;
    priorityPopup = { taskId, top, left: popupLeft(rect.left, 160) };
    statusPopup = null;
    registerPopup(() => { priorityPopup = null; });
  }

  async function setPriority(taskId: string, priority: TaskPriority) {
    priorityPopup = null;
    await updateTask(taskId, { priority });
  }

  // ── Task actions ─────────────────────────────────────────────────────────
  async function updateTask(id: string, data: Parameters<typeof tasksApi.update>[1]) {
    await tasksApi.update(id, data);
    onUpdate();
  }

  async function deleteTask(task: Task) {
    if (!confirm($t('task.deleteConfirm'))) return;
    await tasksApi.delete(task.id);
    onUpdate();
  }

  // ── Assignee popup ────────────────────────────────────────────────────────
  let assigneePopup = $state<{ taskId: string; top: number; left: number } | null>(null);
  const assigneeMembers = $derived<ProjectMember[]>(project.members ?? []);
  let assigneeQuery = $state('');

  const filteredAssigneeMembers = $derived(
    assigneeQuery.trim()
      ? assigneeMembers.filter((m) =>
          matchKorean(assigneeQuery, m.user.name) ||
          m.user.email.toLowerCase().includes(assigneeQuery.toLowerCase())
        )
      : assigneeMembers
  );

  function openAssigneePopup(e: MouseEvent, taskId: string) {
    e.stopPropagation();
    if (assigneePopup?.taskId === taskId) { assigneePopup = null; closeActivePopup(); return; }
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const popupH = 280;
    const top = rect.bottom + 4 + popupH > window.innerHeight ? rect.top - popupH - 4 : rect.bottom + 4;
    assigneePopup = { taskId, top, left: popupLeft(rect.left, 220) };
    assigneeQuery = '';
    statusPopup = null;
    priorityPopup = null;
    registerPopup(() => { assigneePopup = null; });
  }

  async function changeAssignee(taskId: string, user: User | null) {
    assigneePopup = null;
    await tasksApi.update(taskId, { assignee_id: user?.id ?? null });
    onUpdate();
  }

  // ── DnD per group ────────────────────────────────────────────────────────
  function handleConsider(e: CustomEvent, status: TaskStatus) {
    const { items, info } = e.detail;
    if (info.trigger === TRIGGERS.DRAG_STARTED) {
      const task = tasks.find((t) => t.id === info.id);
      if (task) draggingTask.set(task);
    }
    groups = { ...groups, [status]: items };
  }

  async function handleFinalize(e: CustomEvent, status: TaskStatus) {
    // If onUp already handled a sidebar project drop, just restore groups and bail.
    if (sidebarDropHandled) {
      sidebarDropHandled = false;
      groups = buildGroups(applySortKey(tasks, sortKey, sortDir));
      return;
    }

    // Capture both stores BEFORE clearing them, to avoid reactive effect timing issues
    const task = get(draggingTask);
    const capturedProjectId = get(sidebarHoverProjectId);
    draggingTask.set(null);

    const newItems: Task[] = e.detail.items;
    const taskId: string   = e.detail.info.id;
    const trigger: string  = e.detail.info.trigger;

    groups = { ...groups, [status]: newItems as any };

    // Cross-project drop → sidebar
    if (trigger === TRIGGERS.DROPPED_OUTSIDE_OF_ANY) {
      if (task) await handleDroppedOutside(task, capturedProjectId);
      return;
    }

    // Shadow item not present → source group, skip
    if (!newItems.some((t) => t.id === taskId)) return;

    // Clear column sort on manual reorder
    sortKey = null;
    saveSort(null, sortDir);

    const idx   = newItems.findIndex((t) => t.id === taskId);
    const above = newItems[idx - 1];
    const below = newItems[idx + 1];
    const sort_order =
      above && below ? (above.sort_order + below.sort_order) / 2
      : above         ? above.sort_order + 1000
      : below         ? below.sort_order - 1000
      : 1000;

    try {
      await tasksApi.move(taskId, status, sort_order);
      onUpdate();
    } catch {
      groups = buildGroups(applySortKey(tasks, null, 'asc'));
    }
  }

  // ── DnD: cross-project drop via sidebar ──────────────────────────────────
  async function handleDroppedOutside(task: Task, targetProjectId: string | null = get(sidebarHoverProjectId)) {
    sidebarHoverProjectId.set(null);

    if (!targetProjectId || targetProjectId === project.id) {
      groups = buildGroups(applySortKey(tasks, sortKey, sortDir));
      return;
    }

    const targetProject = projects.find((p) => p.id === targetProjectId);
    if (!targetProject) {
      groups = buildGroups(applySortKey(tasks, sortKey, sortDir));
      return;
    }

    const isStatusActive = !targetProject.disabled_statuses?.includes(task.status);
    const firstActive = TASK_STATUSES.find((s) => !targetProject.disabled_statuses?.includes(s.value));
    const finalStatus = isStatusActive ? task.status : (firstActive?.value ?? 'backlog');

    try {
      await tasksApi.move(task.id, finalStatus, Date.now(), targetProjectId);
      onUpdate();
      const statusLabel = TASK_STATUSES.find((s) => s.value === finalStatus)?.label ?? finalStatus;
      if (!isStatusActive) {
        toastStore.add(`"${task.title}" → ${targetProject.name} / ${statusLabel} (카테고리 비활성으로 이동됨)`, 'info');
      } else {
        toastStore.add(`"${task.title}" → ${targetProject.name} / ${statusLabel}`, 'success');
      }
    } catch {
      toastStore.add('이슈 이동에 실패했습니다.', 'error');
      groups = buildGroups(applySortKey(tasks, sortKey, sortDir));
    }
  }

  const FLIP_MS = 150;

  const COL_HEADERS = $derived([
    { key: 'title' as SortKey,    label: $t('table.task') },
    { key: 'priority' as SortKey, label: $t('table.priority') },
  ]);

  // ── Narrow viewport (≤540px) ─────────────────────────────────────────────
  let narrow = $state(false);
  $effect(() => {
    const mq = window.matchMedia('(max-width: 540px)');
    narrow = mq.matches;
    const handler = (e: MediaQueryListEvent) => { narrow = e.matches; };
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  });

  // CJK 문자(한국어·일본어·중국어)는 2유닛, 나머지는 1유닛으로 계산해 컬럼 최소 너비 반환
  function headerColW(label: string): number {
    let units = 0;
    for (const ch of label) {
      const cp = ch.codePointAt(0) ?? 0;
      if (
        (cp >= 0x1100 && cp <= 0x11FF) || // 한글 자모
        (cp >= 0x3040 && cp <= 0x30FF) || // 히라가나·가타카나
        (cp >= 0x3130 && cp <= 0x318F) || // 한글 호환 자모
        (cp >= 0x3400 && cp <= 0x4DBF) || // CJK 확장 A
        (cp >= 0x4E00 && cp <= 0x9FFF) || // CJK 통합 한자
        (cp >= 0xAC00 && cp <= 0xD7AF)    // 한글 음절
      ) {
        units += 2;
      } else if (cp > 32) {
        units += 1;
      }
    }
    return units * 7 + 24; // 7px/유닛 + 양쪽 padding
  }

  const gridCols = $derived.by(() => {
    const priW = headerColW($t('table.priority'));
    const dueW = Math.max(headerColW($t('task.dueDate')), 64);
    const asgW = headerColW($t('table.assignee'));
    const dateW = headerColW($t('table.createdAt'));
    return narrow
      ? `28px 72px 1fr ${priW}px ${dueW}px ${asgW}px`
      : `28px 72px 1fr ${priW}px ${dueW}px ${asgW}px ${dateW}px`;
  });
</script>

<svelte:window onclick={() => closeActivePopup()} />

<div class="h-full overflow-auto scrollbar-thin bg-white dark:bg-slate-900">
<div class="flex flex-col {narrow ? '' : 'min-w-[580px]'}">
  <!-- Column header -->
  <div class="sticky top-0 z-10 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700
              grid gap-0 items-center px-2
              text-xs font-semibold text-slate-500 dark:text-slate-400 select-none"
    style="grid-template-columns: {gridCols}"
  >
    <div class="py-3 flex items-center justify-center">
      {#if sortKey === null}
        <span class="text-slate-300 dark:text-slate-600 text-base leading-none" title="수동 정렬 중">⠿</span>
      {/if}
    </div>
    <div class="py-3 px-2 whitespace-nowrap">REF</div>
    {#each COL_HEADERS as col}
      <button
        class="py-3 px-2 text-left hover:text-slate-700 dark:hover:text-slate-200 transition-colors w-full whitespace-nowrap"
        onclick={() => toggleSort(col.key)}
      >{col.label}{sortIcon(col.key)}</button>
    {/each}
    <div class="py-3 px-2 text-center whitespace-nowrap">{$t('task.dueDate')}</div>
    <div class="py-3 px-2 text-center whitespace-nowrap">{$t('table.assignee')}</div>
    {#if !narrow}
      <button
        class="py-3 px-2 text-left hover:text-slate-700 dark:hover:text-slate-200 transition-colors w-full whitespace-nowrap"
        onclick={() => toggleSort('created_at')}
      >{$t('table.createdAt')}{sortIcon('created_at')}</button>
    {/if}
  </div>

  <!-- Status groups -->
  {#each TASK_STATUSES as statusCfg}
    {@const groupItems = groups[statusCfg.value] ?? []}
    {@const visibleCount = groupItems.filter((t) => !(t as any).isDndShadowItem).length}

    <!-- Group header -->
    {@const isCollapsed = collapsed.has(statusCfg.value) && headerDragOver !== statusCfg.value}
    <button
      type="button"
      onclick={() => toggleCollapse(statusCfg.value)}
      data-status-header={statusCfg.value}
      class="sticky top-[37px] z-[5] w-full border-b border-t px-4 py-1.5 flex items-center gap-2 select-none transition-colors cursor-pointer [&>*]:pointer-events-none
             {headerDragOver === statusCfg.value
               ? 'bg-brand-300 dark:bg-brand-500 border-slate-200 dark:border-slate-700 shadow-[0_0_0_2px_theme(colors.indigo.400)] dark:shadow-[0_0_0_2px_theme(colors.indigo.400)] z-[6]'
               : 'bg-slate-100 dark:bg-slate-800 border-slate-200 dark:border-slate-700 hover:bg-slate-200/60 dark:hover:bg-slate-700/60'}"
    >
      <svg
        class="w-3 h-3 transition-transform {isCollapsed ? '-rotate-90' : ''}
               {headerDragOver === statusCfg.value ? 'text-brand-600 dark:text-brand-300' : 'text-slate-400 dark:text-slate-500'}"
        viewBox="0 0 10 6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"
      >
        <polyline points="1,1 5,5 9,1"/>
      </svg>
      <span class="inline-block px-2 py-0.5 rounded-full text-xs font-medium {statusCfg.color} {statusCfg.bg}">
        {$t(`status.${statusCfg.value}` as any)}
      </span>
      <span class="text-xs text-slate-400 dark:text-slate-500">{visibleCount}</span>
    </button>

    <!-- Group rows - always rendered so collapsed groups still accept drops -->
    <div
      use:dndzone={{
        items: groupItems,
        type: 'table-task',
        flipDurationMs: FLIP_MS,
        dropTargetStyle: { outline: 'none', background: 'rgba(99,102,241,0.04)' },
        transformDraggedElement: (el: HTMLElement | undefined) => {
          if (!el) return;
          if (!el.dataset.frozenWidth) el.dataset.frozenWidth = String(el.offsetWidth);
          el.style.width = el.dataset.frozenWidth + 'px';
          el.style.boxSizing = 'border-box';
        },
      }}
      onconsider={(e: CustomEvent) => handleConsider(e, statusCfg.value)}
      onfinalize={(e: CustomEvent) => handleFinalize(e, statusCfg.value)}
      class="{isCollapsed ? 'min-h-[6px]' : 'min-h-[8px]'}"
    >
      {#each groupItems as task (task.id)}
        {@const isShadow = (task as any).isDndShadowItem}
        <div animate:flip={{ duration: FLIP_MS }}>
          {#if isShadow}
            <div class="h-10 mx-2 my-0.5 rounded-lg border-2 border-dashed border-brand-400/50 dark:border-brand-400/30 bg-brand-50/30 dark:bg-brand-500/5"></div>
          {:else if !isCollapsed}
            {@const priorityCfg = PRIORITY_CONFIG.find((p) => p.value === task.priority)!}
            <div
              class="grid gap-0 items-center px-2 border-b border-slate-100 dark:border-slate-800
                     hover:bg-slate-50 dark:hover:bg-slate-800/50 group transition-colors cursor-default"
              style="grid-template-columns: {gridCols}"
            >
              <!-- Drag handle -->
              <div class="flex items-center justify-center py-2.5 cursor-grab active:cursor-grabbing text-slate-300 dark:text-slate-600 hover:text-slate-400 dark:hover:text-slate-500 text-base leading-none select-none">
                ⠿
              </div>

              <!-- Ref -->
              <div class="py-2.5 px-2">
                <span class="text-[11px] font-mono text-slate-400 dark:text-slate-500">{task.ref}</span>
              </div>

              <!-- Title -->
              <div class="py-2.5 px-2 min-w-0 flex items-center gap-1.5">
                <button
                  class="text-left text-sm font-medium text-slate-700 dark:text-slate-200 hover:text-brand-600 dark:hover:text-brand-400 transition-colors truncate block"
                  onclick={() => goto(`/app/project/${task.project_id}/issue/${task.id}`)}
                >{task.title}</button>
                {#if getSubtasks(task).length > 0}
                  {@const total = getSubtasks(task).length}
                  {@const done = getSubtasks(task).filter((s) => s.status === 'done').length}
                  <span class="shrink-0 text-[10px] font-medium px-1.5 py-0.5 rounded-full
                    {done === total
                      ? 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400'
                      : 'bg-slate-100 text-slate-500 dark:bg-slate-700 dark:text-slate-400'}">
                    {Math.round(done / total * 100)}%
                  </span>
                {/if}
              </div>

              <!-- Priority -->
              <div class="py-2 px-2">
                <button
                  onclick={(e) => openPriorityPopup(e, task.id)}
                  class="flex items-center gap-1 text-xs cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-700 rounded px-1 py-0.5 transition-colors whitespace-nowrap"
                >
                  <span class="text-sm leading-none">{priorityCfg.icon}</span>
                  {#if !narrow}<span class="text-slate-600 dark:text-slate-300">{$t(`priority.${task.priority}` as any)}</span>{/if}
                  <svg class="w-2.5 h-2.5 text-slate-400 opacity-70" viewBox="0 0 10 6" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="1,1 5,5 9,1"/>
                  </svg>
                </button>
              </div>

              <!-- Due Date -->
              <div class="py-2 px-2 flex justify-center" onclick={(e) => e.stopPropagation()}>
                <DatePicker
                  plain
                  value={task.due_date ?? ''}
                  onChange={async (v) => { await tasksApi.update(task.id, { due_date: v || null }); onUpdate(); }}
                />
              </div>

              <!-- Assignee -->
              <div class="py-2 px-2 flex items-center justify-center">
                <button
                  onclick={(e) => openAssigneePopup(e, task.id)}
                  title={task.assignee?.name ?? $t('assignee.none')}
                  class="w-7 h-7 rounded-full overflow-hidden flex items-center justify-center hover:ring-2 hover:ring-brand-400 hover:ring-offset-1 transition-all shrink-0"
                >
                  {#if task.assignee?.avatar_url}
                    <img src={task.assignee.avatar_url} class="w-full h-full object-cover" alt={task.assignee.name} />
                  {:else if task.assignee}
                    <div class="w-full h-full bg-brand-400 text-white text-[10px] flex items-center justify-center">
                      {task.assignee.name[0]}
                    </div>
                  {:else}
                    <div class="w-full h-full bg-slate-100 dark:bg-slate-700 text-slate-400 dark:text-slate-500 flex items-center justify-center text-[11px]">
                      +
                    </div>
                  {/if}
                </button>
              </div>

              <!-- Date -->
              {#if !narrow}
                <div class="py-2.5 px-2 text-xs text-slate-400 dark:text-slate-500 whitespace-nowrap">
                  {new Date(task.created_at).toLocaleDateString($dateLocale, { month: 'short', day: 'numeric' })}
                </div>
              {/if}

            </div>

            <!-- Subtask rows (ㄴ hierarchy) -->
            {#if getSubtasks(task).length}
              {#each getSubtasks(task) as sub (sub.id)}
                <div
                  class="grid gap-0 items-center px-2 border-b border-slate-100/60 dark:border-slate-800/60
                         bg-slate-50/50 dark:bg-slate-900/30 hover:bg-slate-100/50 dark:hover:bg-slate-800/30 transition-colors"
                  style="grid-template-columns: {gridCols}"
                >
                  <div></div>
                  <div class="py-2 px-2">
                    <span class="text-[10px] font-mono text-slate-300 dark:text-slate-600">{sub.ref}</span>
                  </div>
                  <div class="py-2 px-2 min-w-0 flex items-center gap-1.5">
                    <span class="text-slate-300 dark:text-slate-600 text-sm leading-none shrink-0 select-none">ㄴ</span>
                    <input
                      type="checkbox"
                      checked={sub.status === 'done'}
                      onchange={() => toggleSubtaskInTable(task, sub)}
                      class="w-3.5 h-3.5 shrink-0 rounded border-slate-300 dark:border-slate-600 text-brand-500 focus:ring-brand-500 cursor-pointer"
                    />
                    <span class="text-xs text-slate-600 dark:text-slate-300 {sub.status === 'done' ? 'line-through text-slate-400 dark:text-slate-500' : ''} truncate">
                      {sub.title}
                    </span>
                  </div>
                  <div></div>
                  <div></div>
                  <div class="py-2 px-2 flex items-center justify-center">
                    {#if sub.assignee}
                      <div class="w-6 h-6 rounded-full overflow-hidden shrink-0" title={sub.assignee.name}>
                        {#if sub.assignee.avatar_url}
                          <img src={sub.assignee.avatar_url} class="w-full h-full object-cover" alt="" />
                        {:else}
                          <div class="w-full h-full bg-brand-400 text-white text-[9px] flex items-center justify-center">
                            {sub.assignee.name[0]}
                          </div>
                        {/if}
                      </div>
                    {:else}
                      <div class="w-6 h-6"></div>
                    {/if}
                  </div>
                  {#if !narrow}<div></div>{/if}
                </div>
              {/each}
            {/if}
          {/if}
        </div>
      {/each}
    </div>
  {/each}

  {#if tasks.length === 0}
    <div class="flex flex-col items-center justify-center py-20 text-slate-400 dark:text-slate-600">
      <p class="text-sm">{$t('task.noTasks')}</p>
    </div>
  {/if}
</div>
</div>

{#if statusPopup}
  {@const popup = statusPopup}
  <div
    onclick={(e) => e.stopPropagation()}
    style="position: fixed; top: {popup.top}px; left: {popup.left}px;"
    class="z-[200] bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-xl shadow-lg overflow-hidden min-w-[130px] py-1"
  >
    {#each TASK_STATUSES as s}
      <button
        onclick={() => setStatus(popup.taskId, s.value)}
        class="w-full flex items-center gap-2 px-3 py-2 text-xs transition-colors hover:bg-slate-50 dark:hover:bg-slate-700"
      >
        <span class="inline-block px-2 py-0.5 rounded-full font-medium {s.color} {s.bg}">
          {$t(`status.${s.value}` as any)}
        </span>
      </button>
    {/each}
  </div>
{/if}

{#if priorityPopup}
  {@const popup = priorityPopup}
  <div
    onclick={(e) => e.stopPropagation()}
    style="position: fixed; top: {popup.top}px; left: {popup.left}px;"
    class="z-[200] bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-xl shadow-lg overflow-hidden min-w-[140px] py-1"
  >
    {#each PRIORITY_CONFIG as p}
      <button
        onclick={() => setPriority(popup.taskId, p.value)}
        class="w-full flex items-center gap-2 px-3 py-2 text-sm transition-colors hover:bg-slate-50 dark:hover:bg-slate-700"
      >
        <span class="text-base leading-none">{p.icon}</span>
        <span class="text-slate-700 dark:text-slate-200">{$t(`priority.${p.value}` as any)}</span>
      </button>
    {/each}
  </div>
{/if}

{#if assigneePopup}
  {@const popup = assigneePopup}
  <div
    onclick={(e) => e.stopPropagation()}
    style="position: fixed; top: {popup.top}px; left: {popup.left}px; width: 220px;"
    class="z-[200] bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-xl shadow-lg overflow-hidden"
  >
    <div class="p-2 border-b border-slate-100 dark:border-slate-700">
      <input
        bind:value={assigneeQuery}
        placeholder={$t('assignee.search')}
        autofocus
        class="w-full text-sm px-2 py-1 bg-slate-50 dark:bg-slate-700 text-slate-800 dark:text-slate-100 placeholder:text-slate-400 rounded-lg border-0 focus:outline-none focus:ring-2 focus:ring-brand-500"
      />
    </div>
    <ul class="max-h-52 overflow-y-auto scrollbar-thin py-1">
      <li>
        <button
          onclick={() => changeAssignee(popup.taskId, null)}
          class="w-full flex items-center gap-2.5 px-3 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
        >
          <div class="w-6 h-6 rounded-full bg-slate-200 dark:bg-slate-600 flex items-center justify-center text-slate-400 text-xs shrink-0">-</div>
          <span class="text-slate-500 dark:text-slate-400">{$t('assignee.none')}</span>
        </button>
      </li>
      {#each filteredAssigneeMembers as m (m.user.id)}
        <li>
          <button
            onclick={() => changeAssignee(popup.taskId, m.user)}
            class="w-full flex items-center gap-2.5 px-3 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
          >
            {#if m.user.avatar_url}
              <img src={m.user.avatar_url} class="w-6 h-6 rounded-full shrink-0" alt="" />
            {:else}
              <div class="w-6 h-6 rounded-full bg-brand-400 text-white text-[10px] flex items-center justify-center shrink-0">
                {(m.user.name || m.user.email)[0]}
              </div>
            {/if}
            <div class="flex-1 min-w-0 text-left">
              <p class="text-sm font-medium text-slate-700 dark:text-slate-200 truncate">{m.user.name || m.user.email}</p>
              {#if m.user.name}
                <p class="text-xs text-slate-400 dark:text-slate-500 truncate">{m.user.email}</p>
              {/if}
            </div>
          </button>
        </li>
      {/each}
      {#if filteredAssigneeMembers.length === 0 && assigneeQuery.trim()}
        <li class="px-3 py-3 text-sm text-slate-400 dark:text-slate-500 text-center">{$t('assignee.noResults')}</li>
      {/if}
    </ul>
  </div>
{/if}
