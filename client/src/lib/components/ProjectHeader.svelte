<script lang="ts">
  import { page } from '$app/stores';
  import { viewMode } from '$lib/stores/ui';
  import { authStore } from '$lib/stores/auth';
  import { projectsApi } from '$lib/api/projects';
  import type { ProjectMember } from '$lib/types';
  import TaskModal from './TaskModal.svelte';
  import MembersModal from './MembersModal.svelte';
  import { t } from '$lib/i18n';

  const { projectId, onTaskCreated }: { projectId: string; onTaskCreated: () => void } = $props();

  let showCreate = $state(false);
  let showMembers = $state(false);
  let members = $state<ProjectMember[]>([]);

  const project = $derived(
    ($page.data as any)?.projects?.find((p: any) => p.id === projectId) ?? null
  );

  const isOwner = $derived(
    project != null && $authStore.user != null && project.owner.id === $authStore.user.id
  );

  const MAX_AVATARS = 4;
  const visible = $derived(members.slice(0, MAX_AVATARS));
  const overflow = $derived(Math.max(0, members.length - MAX_AVATARS));

  $effect(() => {
    if (projectId) {
      projectsApi.listMembers(projectId).then((m) => (members = m));
    }
  });

  function onMembersClose() {
    // 멤버 변경 후 다시 로드
    projectsApi.listMembers(projectId).then((m) => (members = m));
    showMembers = false;
  }
</script>

<header class="flex items-center justify-between px-6 py-3 border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 shrink-0">
  <div class="flex items-center gap-3">
    {#if project}
      <span class="w-3 h-3 rounded-full" style="background-color: {project.color}"></span>
    {/if}
    <h1 class="text-base font-semibold text-slate-800 dark:text-slate-100">{project?.name ?? '...'}</h1>
  </div>

  <div class="flex items-center gap-2">
    <!-- View toggle -->
    <div class="flex items-center bg-slate-100 dark:bg-slate-800 rounded-lg p-0.5">
      <button
        onclick={() => viewMode.set('board')}
        class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-all {
          $viewMode === 'board'
            ? 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-sm'
            : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'
        }"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
        </svg>
        {$t('view.board')}
      </button>
      <button
        onclick={() => viewMode.set('table')}
        class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-all {
          $viewMode === 'table'
            ? 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-sm'
            : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'
        }"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
        {$t('view.table')}
      </button>
    </div>

    <!-- Member avatar stack -->
    <button
      onclick={() => (showMembers = true)}
      class="flex items-center hover:opacity-80 transition-opacity"
      title={$t('member.manage')}
    >
      <div class="flex items-center">
        {#each visible as m, i (m.user.id)}
          <div
            class="w-5 h-5 rounded-full ring-2 ring-white dark:ring-slate-900 shrink-0 overflow-hidden -ml-1.5 first:ml-0"
            style="z-index: {visible.length - i}"
            title={m.user.name || m.user.email}
          >
            {#if m.user.avatar_url}
              <img src={m.user.avatar_url} alt={m.user.name} class="w-full h-full object-cover" />
            {:else}
              <div class="w-full h-full bg-brand-400 flex items-center justify-center text-white text-[9px] font-medium">
                {(m.user.name || m.user.email)[0].toUpperCase()}
              </div>
            {/if}
          </div>
        {/each}
        {#if overflow > 0}
          <div
            class="w-5 h-5 rounded-full ring-2 ring-white dark:ring-slate-900 bg-slate-200 dark:bg-slate-600 flex items-center justify-center text-[9px] font-medium text-slate-600 dark:text-slate-300 -ml-1.5 shrink-0"
          >+{overflow}</div>
        {/if}
      </div>
    </button>

    <!-- Create task -->
    <button
      onclick={() => (showCreate = true)}
      class="flex items-center gap-1.5 px-3 py-1.5 bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium rounded-lg transition-colors"
    >
      <span class="text-base leading-none">+</span>
      {$t('task.add')}
    </button>
  </div>
</header>

{#if showCreate}
  <TaskModal
    {projectId}
    onClose={() => (showCreate = false)}
    onCreated={() => { showCreate = false; onTaskCreated(); }}
  />
{/if}

{#if showMembers}
  <MembersModal
    {projectId}
    {isOwner}
    onClose={onMembersClose}
  />
{/if}
