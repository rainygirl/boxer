<script lang="ts">
  import { goto, invalidate } from '$app/navigation';
  import TaskDetailPanel from '$lib/components/TaskDetailPanel.svelte';

  const { data } = $props();

  const projectUrl = `/app/project/${data.task.project_id}`;

  function handleClose() {
    goto(projectUrl);
  }

  async function handleUpdate() {
    await invalidate(`tasks:${data.task.project_id}`);
    goto(projectUrl);
  }
</script>

<TaskDetailPanel task={data.task} onClose={handleClose} onUpdate={handleUpdate} />
