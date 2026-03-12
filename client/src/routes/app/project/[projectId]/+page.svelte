<script lang="ts">
  import { invalidate } from '$app/navigation';
  import { page } from '$app/stores';
  import { viewMode } from '$lib/stores/ui';
  import type { Task } from '$lib/types';
  import ProjectHeader from '$lib/components/ProjectHeader.svelte';
  import KanbanBoard from '$lib/components/KanbanBoard.svelte';
  import TaskTable from '$lib/components/TaskTable.svelte';
  import TaskDetailPanel from '$lib/components/TaskDetailPanel.svelte';

  const { data } = $props();

  const refresh = () => invalidate(`tasks:${data.projectId}`);

  const currentProject = $derived(
    (data.projects as any[])?.find((p: any) => p.id === data.projectId)
  );

  // ── Permalink: ?task=[taskId] — read once at init, not reactive ───────────
  const initialTaskId = $page.url.searchParams.get('task');
  let permalinkTask = $state<Task | null>(
    initialTaskId
      ? ((data.tasks as Task[]).find((t) => t.id === initialTaskId) ?? null)
      : null
  );

  function closePermalinkTask() {
    permalinkTask = null;
    const url = new URL(window.location.href);
    url.searchParams.delete('task');
    history.replaceState({}, '', url.toString());
  }
</script>

<ProjectHeader projectId={data.projectId} onTaskCreated={refresh} />

<div class="flex-1 overflow-hidden">
  {#if $viewMode === 'board'}
    {#if currentProject}
      <KanbanBoard project={currentProject} projects={data.projects as any} tasks={data.tasks} onUpdate={refresh} />
    {/if}
  {:else}
    {#if currentProject}
      <TaskTable project={currentProject} projects={data.projects as any} tasks={data.tasks} onUpdate={refresh} />
    {/if}
  {/if}
</div>

{#if permalinkTask}
  <TaskDetailPanel
    task={permalinkTask}
    onClose={closePermalinkTask}
    onUpdate={() => { closePermalinkTask(); refresh(); }}
  />
{/if}
