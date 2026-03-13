<script lang="ts">
  import { page } from '$app/stores';
  import { invalidate } from '$app/navigation';
  import { viewMode } from '$lib/stores/ui';
  import { authStore } from '$lib/stores/auth';
  import { projectsApi } from '$lib/api/projects';
  import type { ProjectMember } from '$lib/types';
  import TaskModal from './TaskModal.svelte';
  import MembersModal from './MembersModal.svelte';
  import ProjectSettingsModal from './ProjectSettingsModal.svelte';
  import { t } from '$lib/i18n';
  import { sidebarOpen } from '$lib/stores/sidebar';

  const { projectId, onTaskCreated, section = 'issues' }: { projectId: string; onTaskCreated: () => void; section?: 'issues' | 'reports' } = $props();

  let showCreate = $state(false);
  let showMembers = $state(false);
  let showSettings = $state(false);
  let showColorPicker = $state(false);
  const COLORS = ['#6366f1','#8b5cf6','#ec4899','#ef4444','#f97316','#eab308','#22c55e','#14b8a6','#3b82f6','#64748b'];

  const project = $derived(
    ($page.data as any)?.projects?.find((p: any) => p.id === projectId) ?? null
  );

  const isOwner = $derived(
    project != null && $authStore.user != null && project.owner.id === $authStore.user.id
  );

  const MAX_AVATARS = 4;
  const members = $derived<ProjectMember[]>(project?.members ?? []);
  const visible = $derived(members.slice(0, MAX_AVATARS));
  const overflow = $derived(Math.max(0, members.length - MAX_AVATARS));

  async function onMembersClose() {
    await invalidate('app:projects');
    showMembers = false;
  }

  async function setColor(color: string) {
    showColorPicker = false;
    if (color === project?.color) return;
    await projectsApi.update(projectId, { color });
    await invalidate('app:projects');
  }
</script>

<svelte:window onclick={() => { showColorPicker = false; }} />

<header class="flex items-center justify-between px-3 md:px-6 py-3 border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 shrink-0">
  <!-- Left: hamburger(mobile) · color · name · members · settings -->
  <div class="flex items-center gap-2">
    <!-- Hamburger (mobile only) -->
    <button
      class="md:hidden p-1.5 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
      onclick={() => sidebarOpen.update((v) => !v)}
    >
      <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
      </svg>
    </button>
    {#if project}
      <!-- Color dot (owner only: clickable) -->
      <div class="relative">
        {#if isOwner}
          <button
            onclick={(e) => { e.stopPropagation(); showColorPicker = !showColorPicker; }}
            class="w-3.5 h-3.5 rounded-full ring-2 ring-transparent hover:ring-slate-300 dark:hover:ring-slate-600 transition-all"
            style="background-color: {project.color}"
            title="색상 변경"
          ></button>
          {#if showColorPicker}
            <div
              onclick={(e) => e.stopPropagation()}
              class="absolute top-full left-0 mt-2 z-50 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-lg p-2.5 flex flex-wrap gap-1.5 w-[136px]"
            >
              {#each COLORS as c}
                <button
                  onclick={() => setColor(c)}
                  class="w-6 h-6 rounded-full transition-all {project.color === c ? 'ring-2 ring-offset-1 ring-slate-400 scale-110' : 'hover:scale-110'}"
                  style="background-color: {c}"
                ></button>
              {/each}
            </div>
          {/if}
        {:else}
          <span class="w-3.5 h-3.5 rounded-full block" style="background-color: {project.color}"></span>
        {/if}
      </div>
    {/if}

    <h1 class="text-base font-semibold text-slate-800 dark:text-slate-100">{project?.name ?? '...'}</h1>

    <!-- Member avatar stack -->
    <button
      onclick={() => (showMembers = true)}
      class="flex items-center ml-1 hover:opacity-80 transition-opacity"
      title={$t('member.manage')}
    >
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
        <div class="w-5 h-5 rounded-full ring-2 ring-white dark:ring-slate-900 bg-slate-200 dark:bg-slate-600 flex items-center justify-center text-[9px] font-medium text-slate-600 dark:text-slate-300 -ml-1.5 shrink-0">
          +{overflow}
        </div>
      {/if}
    </button>

    <!-- Settings gear (owner only) -->
    {#if isOwner && project}
      <button
        onclick={() => (showSettings = true)}
        title="프로젝트 설정"
        class="p-1 text-slate-400 dark:text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
      >
        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round"
            d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      </button>
    {/if}
  </div>

  <!-- Right: view toggle · create task -->
  <div class="flex items-center gap-2">
    {#if section === 'issues'}
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
        <span class="hidden sm:inline">{$t('view.board')}</span>
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
        <span class="hidden sm:inline">{$t('view.table')}</span>
      </button>
    </div>

    <!-- Create task -->
    <button
      onclick={() => (showCreate = true)}
      class="flex items-center gap-1.5 px-3 py-1.5 bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium rounded-lg transition-colors"
    >
      <span class="text-base leading-none">+</span>
      <span class="hidden sm:inline">{$t('task.add')}</span>
    </button>
    {/if}
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

{#if showSettings && project}
  <ProjectSettingsModal {project} onClose={() => (showSettings = false)} onOpenMembers={() => (showMembers = true)} />
{/if}
