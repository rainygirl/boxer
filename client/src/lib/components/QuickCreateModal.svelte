<script lang="ts">
  import { goto } from '$app/navigation';
  import { tasksApi } from '$lib/api/tasks';
  import { TASK_STATUSES } from '$lib/types';
  import type { Project, TaskStatus } from '$lib/types';

  const { onClose, projects }: { onClose: () => void; projects: Project[] } = $props();

  let selectedProjectId = $state(projects[0]?.id ?? '');
  let title = $state('');
  let status = $state<TaskStatus>('todo');
  let saving = $state(false);
  let titleEl = $state<HTMLInputElement | null>(null);

  $effect(() => {
    setTimeout(() => titleEl?.focus(), 0);
  });

  async function handleSubmit() {
    if (!title.trim() || !selectedProjectId) return;
    saving = true;
    try {
      const task = await tasksApi.create(selectedProjectId, { title: title.trim(), status });
      goto(`/app/project/${selectedProjectId}/issue/${task.id}`);
      onClose();
    } finally {
      saving = false;
    }
  }

  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') onClose();
  }
</script>

<svelte:window onkeydown={onKeydown} />

<div
  class="fixed inset-0 z-[200] flex items-start justify-center pt-[15vh] bg-black/50"
  onclick={onClose}
>
  <div
    class="w-full max-w-lg bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-700 overflow-hidden"
    onclick={(e) => e.stopPropagation()}
  >
    <div class="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
      <h2 class="text-sm font-semibold text-slate-700 dark:text-slate-200">Create Issue</h2>
      <button onclick={onClose} class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 w-6 h-6 flex items-center justify-center rounded hover:bg-slate-100 dark:hover:bg-slate-800 text-sm">✕</button>
    </div>

    <div class="px-5 py-4 space-y-4">
      <!-- Project selector -->
      <div>
        <label class="block text-xs font-medium text-slate-400 dark:text-slate-500 mb-1">Project</label>
        <select
          bind:value={selectedProjectId}
          class="w-full text-sm px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500"
        >
          {#each projects as p (p.id)}
            <option value={p.id}>{p.name}</option>
          {/each}
        </select>
      </div>

      <!-- Title -->
      <div>
        <label class="block text-xs font-medium text-slate-400 dark:text-slate-500 mb-1">Title</label>
        <input
          bind:this={titleEl}
          bind:value={title}
          placeholder="Issue title..."
          onkeydown={(e) => e.key === 'Enter' && handleSubmit()}
          class="w-full text-sm px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
      </div>

      <!-- Status -->
      <div>
        <label class="block text-xs font-medium text-slate-400 dark:text-slate-500 mb-1">Status</label>
        <select
          bind:value={status}
          class="w-full text-sm px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500"
        >
          {#each TASK_STATUSES as s}
            <option value={s.value}>{s.label}</option>
          {/each}
        </select>
      </div>
    </div>

    <div class="px-5 py-3 border-t border-slate-100 dark:border-slate-700 flex items-center justify-end gap-2">
      <button
        onclick={onClose}
        class="text-sm px-3 py-1.5 text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
      >Cancel</button>
      <button
        onclick={handleSubmit}
        disabled={saving || !title.trim() || !selectedProjectId}
        class="text-sm px-4 py-1.5 bg-brand-500 hover:bg-brand-600 text-white rounded-lg transition-colors disabled:opacity-50 font-medium"
      >{saving ? 'Creating...' : 'Create Issue'}</button>
    </div>
  </div>
</div>
