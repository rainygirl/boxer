<script lang="ts">
  import { dndzone, TRIGGERS } from 'svelte-dnd-action';
  import { flip } from 'svelte/animate';
  import type { Task, TaskStatus, TaskPriority, Project } from '$lib/types';
  import { TASK_STATUSES, PRIORITY_CONFIG } from '$lib/types';
  import { tasksApi } from '$lib/api/tasks';
  import { t, dateLocale } from '$lib/i18n';
  import { registerPopup, closeActivePopup, popupLeft } from '$lib/stores/popup';
  import TaskDetailPanel from '$lib/components/TaskDetailPanel.svelte';
  import { projectsApi } from '$lib/api/projects';
  import { matchKorean } from '$lib/utils/hangul';
  import type { User, ProjectMember } from '$lib/types';

  const { data } = $props();

  let tasks = $state<Task[]>(data.tasks);
  const projects: Project[] = data.projects;

  // ── View mode ─────────────────────────────────────────────────────────────
  const VIEW_KEY = 'boxer:my-issues-view';
  let viewMode = $state<'board' | 'table'>(
    (() => { try { const v = localStorage.getItem(VIEW_KEY); return v === 'table' ? 'table' : 'board'; } catch { return 'board'; } })()
  );
  $effect(() => { try { localStorage.setItem(VIEW_KEY, viewMode); } catch {} });

  // ── Helpers ───────────────────────────────────────────────────────────────
  function getProject(id: string): Project | undefined {
    return projects.find((p) => p.id === id);
  }

  async function reload() {
    tasks = await tasksApi.myIssues();
  }

  // ── Selected task (detail panel) ──────────────────────────────────────────
  let selectedTask = $state<Task | null>(null);

  // ── Board ─────────────────────────────────────────────────────────────────
  type GroupMap = Record<string, (Task & { id: string })[]>;

  function buildGroups(list: Task[]): GroupMap {
    const result: GroupMap = {};
    for (const s of TASK_STATUSES) {
      result[s.value] = list.filter((t) => t.status === s.value) as any;
    }
    return result;
  }

  let boardGroups = $state<GroupMap>(buildGroups(tasks));

  $effect(() => { boardGroups = buildGroups(tasks); });

  let draggingId = $state<string | null>(null);

  function boardConsider(e: CustomEvent, status: TaskStatus) {
    const { items, info } = e.detail;
    if (info.trigger === TRIGGERS.DRAG_STARTED) draggingId = info.id;
    boardGroups = { ...boardGroups, [status]: items };
  }

  async function boardFinalize(e: CustomEvent, status: TaskStatus) {
    draggingId = null;
    const newItems: Task[] = e.detail.items;
    const taskId: string  = e.detail.info.id;
    boardGroups = { ...boardGroups, [status]: newItems as any };
    if (!newItems.some((t) => t.id === taskId)) return;

    const idx   = newItems.findIndex((t) => t.id === taskId);
    const above = newItems[idx - 1];
    const below = newItems[idx + 1];
    const sort_order =
      above && below ? (above.sort_order + below.sort_order) / 2
      : above         ? above.sort_order + 1000
      : below         ? below.sort_order - 1000
      : 1000;

    await tasksApi.move(taskId, status, sort_order);
    await reload();
  }

  // ── Table ─────────────────────────────────────────────────────────────────
  type SortKey = 'title' | 'priority' | 'project' | 'created_at';
  const SORT_KEY = 'boxer:my-issues-sort';

  function loadSort() {
    try { const r = localStorage.getItem(SORT_KEY); if (r) return JSON.parse(r); } catch {}
    return { key: null, dir: 'asc' };
  }
  function saveSort(key: SortKey | null, dir: 'asc' | 'desc') {
    try { localStorage.setItem(SORT_KEY, JSON.stringify({ key, dir })); } catch {}
  }

  const initSort = loadSort();
  let sortKey = $state<SortKey | null>(initSort.key);
  let sortDir = $state<'asc' | 'desc'>(initSort.dir);

  const priorityOrder: Record<TaskPriority, number> = { urgent: 0, high: 1, medium: 2, low: 3, none: 4 };

  function applySortKey(list: Task[], key: SortKey | null, dir: 'asc' | 'desc') {
    const arr = [...list];
    if (!key) return arr.sort((a, b) => a.sort_order - b.sort_order);
    arr.sort((a, b) => {
      let cmp = 0;
      if (key === 'title')      cmp = a.title.localeCompare(b.title);
      else if (key === 'priority') cmp = priorityOrder[a.priority] - priorityOrder[b.priority];
      else if (key === 'project')  cmp = (getProject(a.project_id)?.name ?? '').localeCompare(getProject(b.project_id)?.name ?? '');
      else cmp = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
      return dir === 'asc' ? cmp : -cmp;
    });
    return arr;
  }

  function toggleSort(key: SortKey) {
    if (sortKey === key) sortDir = sortDir === 'asc' ? 'desc' : 'asc';
    else { sortKey = key; sortDir = 'asc'; }
    saveSort(sortKey, sortDir);
    tableGroups = buildTableGroups(tasks, sortKey, sortDir);
  }
  function sortIcon(key: SortKey) { return sortKey !== key ? '' : sortDir === 'asc' ? ' ↑' : ' ↓'; }

  // Table groups by status
  type TableGroupMap = Record<string, (Task & { id: string })[]>;
  function buildTableGroups(list: Task[], key: SortKey | null, dir: 'asc' | 'desc'): TableGroupMap {
    const result: TableGroupMap = {};
    for (const s of TASK_STATUSES) {
      result[s.value] = applySortKey(list.filter((t) => t.status === s.value), key, dir) as any;
    }
    return result;
  }

  let tableGroups = $state<TableGroupMap>(buildTableGroups(tasks, initSort.key, initSort.dir));
  $effect(() => { tableGroups = buildTableGroups(tasks, sortKey, sortDir); });

  // Table collapse
  const COLLAPSE_KEY = 'boxer:my-issues-collapse';
  function loadCollapsed() { try { const r = localStorage.getItem(COLLAPSE_KEY); if (r) return new Set<string>(JSON.parse(r)); } catch {} return new Set<string>(); }
  function saveCollapsed(s: Set<string>) { try { localStorage.setItem(COLLAPSE_KEY, JSON.stringify([...s])); } catch {} }
  let collapsed = $state<Set<string>>(loadCollapsed());
  function toggleCollapse(status: string) {
    const next = new Set(collapsed);
    if (next.has(status)) next.delete(status); else next.add(status);
    collapsed = next;
    saveCollapsed(next);
  }

  // Table popups
  let statusPopup = $state<{ taskId: string; top: number; left: number } | null>(null);
  let priorityPopup = $state<{ taskId: string; top: number; left: number } | null>(null);
  let assigneePopup = $state<{ taskId: string; projectId: string; top: number; left: number } | null>(null);
  let assigneeMembers = $state<ProjectMember[]>([]);
  let assigneeQuery = $state('');

  const filteredAssigneeMembers = $derived(
    assigneeQuery.trim()
      ? assigneeMembers.filter((m) =>
          matchKorean(assigneeQuery, m.user.name) ||
          m.user.email.toLowerCase().includes(assigneeQuery.toLowerCase())
        )
      : assigneeMembers
  );
  let tableHeaderDragOver = $state<string | null>(null);

  function openAssigneePopup(e: MouseEvent, task: Task) {
    e.stopPropagation();
    if (assigneePopup?.taskId === task.id) { assigneePopup = null; closeActivePopup(); return; }
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const popupH = 280;
    const top = rect.bottom + 4 + popupH > window.innerHeight ? rect.top - popupH - 4 : rect.bottom + 4;
    assigneePopup = { taskId: task.id, projectId: task.project_id, top, left: popupLeft(rect.left, 220) };
    assigneeQuery = '';
    statusPopup = null;
    priorityPopup = null;
    registerPopup(() => { assigneePopup = null; });
    projectsApi.listMembers(task.project_id).then((m) => (assigneeMembers = m));
  }

  async function changeAssignee(taskId: string, user: User | null) {
    assigneePopup = null;
    await tasksApi.update(taskId, { assignee_id: user?.id ?? null });
    await reload();
  }

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

  async function setStatus(taskId: string, status: TaskStatus) {
    statusPopup = null;
    await tasksApi.update(taskId, { status });
    await reload();
  }

  async function setPriority(taskId: string, priority: TaskPriority) {
    priorityPopup = null;
    await tasksApi.update(taskId, { priority });
    await reload();
  }

  async function deleteTask(task: Task) {
    if (!confirm($t('task.deleteConfirm'))) return;
    await tasksApi.delete(task.id);
    await reload();
  }

  // Table header drag-drop (pointer-based)
  $effect(() => {
    function onMove(e: PointerEvent) {
      if (!draggingId) { tableHeaderDragOver = null; return; }
      const els = document.elementsFromPoint(e.clientX, e.clientY) as HTMLElement[];
      const header = els.find((el) => el.dataset.tableHeader);
      tableHeaderDragOver = header?.dataset.tableHeader ?? null;
    }
    function onUp() {
      const h = tableHeaderDragOver;
      if (!h) return;
      const task = tasks.find((t) => t.id === draggingId);
      tableHeaderDragOver = null;
      draggingId = null;
      if (!task || task.status === h) return;
      tasksApi.move(task.id, h as TaskStatus, task.sort_order).then(() => reload());
    }
    document.addEventListener('pointermove', onMove, { passive: true });
    document.addEventListener('pointerup', onUp);
    return () => {
      document.removeEventListener('pointermove', onMove);
      document.removeEventListener('pointerup', onUp);
    };
  });

  const FLIP_MS = 150;

  function formatDate(isoStr: string): string {
    const d = new Date(isoStr);
    const now = new Date();
    const isToday = d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth() && d.getDate() === now.getDate();
    if (isToday) return d.toLocaleTimeString($dateLocale, { hour: '2-digit', minute: '2-digit' });
    return d.toLocaleDateString($dateLocale, { month: 'short', day: 'numeric' });
  }
</script>

<svelte:window onclick={() => closeActivePopup()} />

<div class="flex flex-col h-full overflow-hidden bg-white dark:bg-slate-900">
  <!-- Header -->
  <div class="flex items-center justify-between px-6 py-3 border-b border-slate-200 dark:border-slate-700 shrink-0">
    <h1 class="text-base font-semibold text-slate-800 dark:text-slate-100">
      {$t('myIssues.title')}
    </h1>
    <div class="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-0.5">
      <button
        onclick={() => (viewMode = 'board')}
        class="px-3 py-1 text-xs font-medium rounded-md transition-colors
               {viewMode === 'board' ? 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-sm' : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'}"
      >{$t('view.board')}</button>
      <button
        onclick={() => (viewMode = 'table')}
        class="px-3 py-1 text-xs font-medium rounded-md transition-colors
               {viewMode === 'table' ? 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-sm' : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'}"
      >{$t('view.table')}</button>
    </div>
  </div>

  <!-- ── BOARD VIEW ──────────────────────────────────────────────────────── -->
  {#if viewMode === 'board'}
    <div class="flex-1 flex gap-3 overflow-x-auto overflow-y-hidden p-4">
      {#each TASK_STATUSES as statusCfg}
        {@const colItems = boardGroups[statusCfg.value] ?? []}
        {@const visibleCount = colItems.filter((t) => !(t as any).isDndShadowItem).length}

        <div class="flex flex-col w-64 shrink-0 rounded-xl bg-slate-50 dark:bg-slate-800/50 overflow-hidden">
          <!-- Column header -->
          <div class="flex items-center gap-2 px-3 py-2.5 border-b border-slate-200 dark:border-slate-700">
            <span class="inline-block px-2 py-0.5 rounded-full text-xs font-medium {statusCfg.color} {statusCfg.bg}">
              {$t(`status.${statusCfg.value}` as any)}
            </span>
            <span class="text-xs text-slate-400">{visibleCount}</span>
          </div>

          <!-- Cards -->
          <div
            use:dndzone={{ items: colItems, type: 'my-issues-board', flipDurationMs: FLIP_MS, dropTargetStyle: {} }}
            onconsider={(e: CustomEvent) => boardConsider(e, statusCfg.value)}
            onfinalize={(e: CustomEvent) => boardFinalize(e, statusCfg.value)}
            class="flex-1 flex flex-col gap-2 p-2 overflow-y-auto scrollbar-thin min-h-[60px]"
          >
            {#each colItems as task (task.id)}
              {@const isShadow = (task as any).isDndShadowItem}
              <div animate:flip={{ duration: FLIP_MS }}>
                {#if isShadow}
                  <div class="h-16 rounded-lg border-2 border-dashed border-brand-400/50 bg-brand-50/30 dark:bg-brand-500/5"></div>
                {:else}
                  {@const proj = getProject(task.project_id)}
                  {@const pCfg = PRIORITY_CONFIG.find((p) => p.value === task.priority)!}
                  <button
                    onclick={() => (selectedTask = task)}
                    class="w-full text-left bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-3 hover:border-brand-300 dark:hover:border-brand-600 hover:shadow-sm transition-all cursor-pointer"
                  >
                    <!-- Project badge -->
                    {#if proj}
                      <div class="flex items-center gap-1.5 mb-2">
                        <span class="w-2 h-2 rounded-full shrink-0" style="background-color: {proj.color}"></span>
                        <span class="text-[10px] font-mono text-slate-400 dark:text-slate-500 truncate">{task.ref}</span>
                        <span class="text-[10px] text-slate-400 dark:text-slate-500 truncate">{proj.name}</span>
                      </div>
                    {/if}
                    <p class="text-sm font-medium text-slate-700 dark:text-slate-200 leading-snug mb-2">{task.title}</p>
                    <div class="flex items-center gap-2 text-xs text-slate-400">
                      <span>{pCfg.icon}</span>
                      <span>{formatDate(task.created_at)}</span>
                    </div>
                  </button>
                {/if}
              </div>
            {/each}
          </div>
        </div>
      {/each}
    </div>

  <!-- ── TABLE VIEW ──────────────────────────────────────────────────────── -->
  {:else}
    <div class="flex-1 overflow-auto scrollbar-thin">
      <!-- Column header -->
      <div class="sticky top-0 z-10 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700
                  grid items-center px-2 text-xs font-semibold text-slate-500 dark:text-slate-400 select-none"
        style="grid-template-columns: 72px 1fr 120px 100px 44px 90px"
      >
        <div class="py-3 px-2">REF</div>
        <button class="py-3 px-2 text-left hover:text-slate-700 dark:hover:text-slate-200 transition-colors" onclick={() => toggleSort('title')}>
          {$t('table.task')}{sortIcon('title')}
        </button>
        <button class="py-3 px-2 text-left hover:text-slate-700 dark:hover:text-slate-200 transition-colors" onclick={() => toggleSort('project')}>
          프로젝트{sortIcon('project')}
        </button>
        <button class="py-3 px-2 text-left hover:text-slate-700 dark:hover:text-slate-200 transition-colors" onclick={() => toggleSort('priority')}>
          {$t('table.priority')}{sortIcon('priority')}
        </button>
        <div class="py-3 px-2 text-center whitespace-nowrap">{$t('table.assignee')}</div>
        <button class="py-3 px-2 text-left hover:text-slate-700 dark:hover:text-slate-200 transition-colors" onclick={() => toggleSort('created_at')}>
          {$t('table.createdAt')}{sortIcon('created_at')}
        </button>
      </div>

      {#each TASK_STATUSES as statusCfg}
        {@const groupItems = tableGroups[statusCfg.value] ?? []}
        {@const isCollapsed = collapsed.has(statusCfg.value) && tableHeaderDragOver !== statusCfg.value}
        {@const visibleCount = groupItems.filter((t) => !(t as any).isDndShadowItem).length}

        <!-- Group header -->
        <button
          type="button"
          onclick={() => toggleCollapse(statusCfg.value)}
          data-table-header={statusCfg.value}
          class="sticky top-[37px] z-[5] w-full border-b border-t px-4 py-1.5 flex items-center gap-2 select-none transition-colors cursor-pointer [&>*]:pointer-events-none
                 {tableHeaderDragOver === statusCfg.value
                   ? 'bg-brand-300 dark:bg-brand-500 border-brand-500 dark:border-brand-300 shadow-[0_0_0_2px_theme(colors.indigo.400)] z-[6]'
                   : 'bg-slate-100 dark:bg-slate-800 border-slate-200 dark:border-slate-700 hover:bg-slate-200/60 dark:hover:bg-slate-700/60'}"
        >
          <svg
            class="w-3 h-3 transition-transform {isCollapsed ? '-rotate-90' : ''}
                   {tableHeaderDragOver === statusCfg.value ? 'text-brand-600 dark:text-brand-300' : 'text-slate-400 dark:text-slate-500'}"
            viewBox="0 0 10 6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"
          ><polyline points="1,1 5,5 9,1"/></svg>
          <span class="inline-block px-2 py-0.5 rounded-full text-xs font-medium {statusCfg.color} {statusCfg.bg}">
            {$t(`status.${statusCfg.value}` as any)}
          </span>
          <span class="text-xs text-slate-400 dark:text-slate-500">{visibleCount}</span>
        </button>

        <!-- Group rows -->
        <div
          use:dndzone={{ items: groupItems, type: 'my-issues-table', flipDurationMs: FLIP_MS, dropTargetStyle: { outline: 'none', background: 'rgba(99,102,241,0.04)' } }}
          onconsider={(e: CustomEvent) => { const { items, info } = e.detail; if (info.trigger === TRIGGERS.DRAG_STARTED) draggingId = info.id; tableGroups = { ...tableGroups, [statusCfg.value]: items }; }}
          onfinalize={(e: CustomEvent) => {
            const newItems: Task[] = e.detail.items;
            const taskId: string = e.detail.info.id;
            tableGroups = { ...tableGroups, [statusCfg.value]: newItems as any };
            draggingId = null;
            if (!newItems.some((t) => t.id === taskId)) return;
            const idx = newItems.findIndex((t) => t.id === taskId);
            const above = newItems[idx - 1], below = newItems[idx + 1];
            const sort_order = above && below ? (above.sort_order + below.sort_order) / 2 : above ? above.sort_order + 1000 : below ? below.sort_order - 1000 : 1000;
            tasksApi.move(taskId, statusCfg.value, sort_order).then(() => reload());
          }}
          class="min-h-[6px]"
        >
          {#each groupItems as task (task.id)}
            {@const isShadow = (task as any).isDndShadowItem}
            <div animate:flip={{ duration: FLIP_MS }}>
              {#if isShadow}
                <div class="h-10 mx-2 my-0.5 rounded-lg border-2 border-dashed border-brand-400/50 bg-brand-50/30 dark:bg-brand-500/5"></div>
              {:else if !isCollapsed}
                {@const proj = getProject(task.project_id)}
                {@const pCfg = PRIORITY_CONFIG.find((p) => p.value === task.priority)!}
                <div
                  class="grid items-center px-2 border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50 group transition-colors"
                  style="grid-template-columns: 72px 1fr 120px 100px 44px 90px"
                >
                  <!-- Ref -->
                  <div class="py-2.5 px-2">
                    <span class="text-[11px] font-mono text-slate-400 dark:text-slate-500">{task.ref}</span>
                  </div>

                  <!-- Title -->
                  <div class="py-2.5 px-2 min-w-0">
                    <button
                      onclick={() => (selectedTask = task)}
                      class="text-left text-sm font-medium text-slate-700 dark:text-slate-200 hover:text-brand-600 dark:hover:text-brand-400 transition-colors truncate w-full block"
                    >{task.title}</button>
                  </div>

                  <!-- Project -->
                  <div class="py-2.5 px-2 min-w-0">
                    {#if proj}
                      <div class="flex items-center gap-1.5">
                        <span class="w-2 h-2 rounded-full shrink-0" style="background-color: {proj.color}"></span>
                        <span class="text-xs text-slate-600 dark:text-slate-400 truncate">{proj.name}</span>
                      </div>
                    {/if}
                  </div>

                  <!-- Priority -->
                  <div class="py-2 px-2">
                    <button
                      onclick={(e) => openPriorityPopup(e, task.id)}
                      class="flex items-center gap-1 text-xs cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-700 rounded px-1 py-0.5 transition-colors whitespace-nowrap"
                    >
                      <span class="text-sm leading-none">{pCfg.icon}</span>
                      <span class="text-slate-600 dark:text-slate-300">{$t(`priority.${task.priority}` as any)}</span>
                      <svg class="w-2.5 h-2.5 text-slate-400 opacity-70" viewBox="0 0 10 6" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="1,1 5,5 9,1"/></svg>
                    </button>
                  </div>

                  <!-- Assignee -->
                  <div class="py-2 px-2 flex items-center justify-center">
                    <button
                      onclick={(e) => openAssigneePopup(e, task)}
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
                        <div class="w-full h-full bg-slate-100 dark:bg-slate-700 text-slate-400 dark:text-slate-500 flex items-center justify-center text-[11px]">+</div>
                      {/if}
                    </button>
                  </div>

                  <!-- Date -->
                  <div class="py-2.5 px-2 text-xs text-slate-400 dark:text-slate-500 whitespace-nowrap">
                    {formatDate(task.created_at)}
                  </div>

                </div>
              {/if}
            </div>
          {/each}
        </div>
      {/each}

      {#if tasks.length === 0}
        <div class="flex flex-col items-center justify-center py-20 text-slate-400 dark:text-slate-600">
          <p class="text-sm">{$t('myIssues.empty')}</p>
        </div>
      {/if}
    </div>
  {/if}
</div>

{#if selectedTask}
  <TaskDetailPanel
    task={selectedTask}
    onClose={() => (selectedTask = null)}
    onUpdate={() => { selectedTask = null; reload(); }}
  />
{/if}

{#if statusPopup}
  {@const popup = statusPopup}
  <div onclick={(e) => e.stopPropagation()} style="position:fixed;top:{popup.top}px;left:{popup.left}px" class="z-[200] bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-xl shadow-lg overflow-hidden min-w-[130px] py-1">
    {#each TASK_STATUSES as s}
      <button onclick={() => setStatus(popup.taskId, s.value)} class="w-full flex items-center gap-2 px-3 py-2 text-xs transition-colors hover:bg-slate-50 dark:hover:bg-slate-700">
        <span class="inline-block px-2 py-0.5 rounded-full font-medium {s.color} {s.bg}">{$t(`status.${s.value}` as any)}</span>
      </button>
    {/each}
  </div>
{/if}

{#if priorityPopup}
  {@const popup = priorityPopup}
  <div onclick={(e) => e.stopPropagation()} style="position:fixed;top:{popup.top}px;left:{popup.left}px" class="z-[200] bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-xl shadow-lg overflow-hidden min-w-[140px] py-1">
    {#each PRIORITY_CONFIG as p}
      <button onclick={() => setPriority(popup.taskId, p.value)} class="w-full flex items-center gap-2 px-3 py-2 text-sm transition-colors hover:bg-slate-50 dark:hover:bg-slate-700">
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
