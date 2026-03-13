<script lang="ts">
  import { goto, invalidate } from '$app/navigation';
  import { page } from '$app/stores';
  import { viewMode } from '$lib/stores/ui';
  import type { Task } from '$lib/types';
  import ProjectHeader from '$lib/components/ProjectHeader.svelte';
  import KanbanBoard from '$lib/components/KanbanBoard.svelte';
  import TaskTable from '$lib/components/TaskTable.svelte';
  import ProjectReports from '$lib/components/ProjectReports.svelte';
  import { t } from '$lib/i18n';

  const { data, children } = $props();

  const refresh = () => invalidate(`tasks:${data.projectId}`);

  const currentProject = $derived(
    (data.projects as any[])?.find((p: any) => p.id === data.projectId)
  );

  // ── Sub-navigation ────────────────────────────────────────────────────
  type Section = 'issues' | 'reports';
  const SECTION_KEY = `boxer:project-section:${data.projectId}`;

  const urlSection = $page.url.searchParams.get('s') as Section | null;
  let section = $state<Section>(
    urlSection === 'reports' ? 'reports'
    : urlSection === 'issues' ? 'issues'
    : (() => { try { const v = localStorage.getItem(SECTION_KEY); return v === 'reports' ? 'reports' : 'issues'; } catch { return 'issues'; } })()
  );

  $effect(() => {
    const s = $page.url.searchParams.get('s') as Section | null;
    if (s === 'issues' || s === 'reports') section = s;
  });

  $effect(() => { try { localStorage.setItem(SECTION_KEY, section); } catch {} });
</script>

<ProjectHeader projectId={data.projectId} onTaskCreated={refresh} {section} />

<!-- Sub-nav -->
<div class="flex items-center gap-1 px-4 border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 shrink-0">
  <button
    onclick={() => (section = 'issues')}
    class="px-3 py-2 text-sm font-medium border-b-2 transition-colors {section === 'issues'
      ? 'border-brand-500 text-brand-600 dark:text-brand-400'
      : 'border-transparent text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'}"
  >{$t('nav.issues')}</button>
  <button
    onclick={() => (section = 'reports')}
    class="px-3 py-2 text-sm font-medium border-b-2 transition-colors {section === 'reports'
      ? 'border-brand-500 text-brand-600 dark:text-brand-400'
      : 'border-transparent text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'}"
  >{$t('nav.reports')}</button>
</div>

{#if section === 'issues'}
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
{:else}
  {#if currentProject}
    <ProjectReports
      tasks={data.tasks}
      onSelectTask={(t: Task) => goto(`/app/project/${data.projectId}/issue/${t.id}`)}
    />
  {/if}
{/if}

{@render children()}
