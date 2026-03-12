<script lang="ts">
  import { invalidate } from '$app/navigation';
  import { viewMode } from '$lib/stores/ui';
  import ProjectHeader from '$lib/components/ProjectHeader.svelte';
  import KanbanBoard from '$lib/components/KanbanBoard.svelte';
  import TaskTable from '$lib/components/TaskTable.svelte';

  const { data } = $props();

  const refresh = () => invalidate(`tasks:${data.projectId}`);
</script>

<ProjectHeader projectId={data.projectId} onTaskCreated={refresh} />

<div class="flex-1 overflow-hidden">
  {#if $viewMode === 'board'}
    <KanbanBoard projectId={data.projectId} tasks={data.tasks} onUpdate={refresh} />
  {:else}
    <TaskTable projectId={data.projectId} tasks={data.tasks} onUpdate={refresh} />
  {/if}
</div>
