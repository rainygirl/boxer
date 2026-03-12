<script lang="ts">
  import { page } from '$app/stores';
  import { invalidate, goto } from '$app/navigation';
  import { authStore } from '$lib/stores/auth';
  import { themeStore } from '$lib/stores/theme';
  import { localeStore } from '$lib/stores/locale';
  import { t } from '$lib/i18n';
  import { get } from 'svelte/store';
  import { projectsApi } from '$lib/api/projects';
  import { authApi } from '$lib/api/auth';
  import type { Project } from '$lib/types';
  import CreateProjectModal from './CreateProjectModal.svelte';

  const { projects }: { projects: Project[] } = $props();

  let showCreate = $state(false);
  let deleting = $state<string | null>(null);
  let showUserMenu = $state(false);
  let editingName = $state(false);
  let nameInput = $state('');
  let savingName = $state(false);

  const currentProjectId = $derived($page.params.projectId);
  const isDark = $derived($themeStore === 'dark');
  const isKo = $derived($localeStore === 'ko');

  async function deleteProject(p: Project) {
    if (!confirm(get(t)('project.deleteConfirm', { name: p.name }))) return;
    deleting = p.id;
    try {
      await projectsApi.delete(p.id);
      await invalidate('app:projects');
      if (currentProjectId === p.id) goto('/app');
    } finally {
      deleting = null;
    }
  }

  function handleLogout() {
    authStore.logout();
    goto('/login');
  }

  function openEditName() {
    nameInput = $authStore.user?.name ?? '';
    editingName = true;
    showUserMenu = false;
  }

  async function saveEditName() {
    if (!nameInput.trim()) return;
    savingName = true;
    try {
      const updated = await authApi.updateProfile(nameInput.trim());
      authStore.setUser(updated);
      editingName = false;
    } finally {
      savingName = false;
    }
  }

  function closeMenu(e: MouseEvent) {
    const target = e.target as HTMLElement;
    if (!target.closest('[data-user-menu]')) {
      showUserMenu = false;
    }
  }
</script>

<svelte:window onclick={closeMenu} />

<aside class="w-60 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-700 flex flex-col h-full shrink-0">
  <!-- Logo -->
  <div class="px-4 py-4 border-b border-slate-100 dark:border-slate-700">
    <div class="flex items-center gap-2">
      <span class="text-xl">📦</span>
      <span class="font-bold text-slate-800 dark:text-slate-100 text-lg">Boxer</span>
    </div>
  </div>

  <!-- Projects -->
  <div class="flex-1 overflow-y-auto py-3 scrollbar-thin">
    <div class="flex items-center justify-between px-4 mb-1">
      <span class="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">{$t('sidebar.projects')}</span>
      <button
        onclick={() => (showCreate = true)}
        class="text-slate-400 hover:text-brand-600 dark:hover:text-brand-400 transition-colors text-lg leading-none"
        title={$t('project.new')}
      >+</button>
    </div>

    <nav class="space-y-0.5 px-2">
      {#each projects as p (p.id)}
        <a
          href="/app/project/{p.id}"
          class="flex items-center gap-2.5 px-2 py-2 rounded-lg text-sm transition-colors group {
            currentProjectId === p.id
              ? 'bg-brand-50 dark:bg-brand-500/10 text-brand-700 dark:text-brand-400 font-medium'
              : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800'
          }"
        >
          <span class="w-2.5 h-2.5 rounded-full shrink-0" style="background-color: {p.color}"></span>
          <span class="flex-1 truncate">{p.name}</span>
          {#if currentProjectId === p.id}
            <button
              onclick={(e) => { e.preventDefault(); deleteProject(p); }}
              disabled={deleting === p.id}
              class="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-red-500 transition-all text-xs px-1"
            >✕</button>
          {/if}
        </a>
      {/each}
    </nav>

    {#if projects.length === 0}
      <p class="px-4 text-xs text-slate-400 dark:text-slate-500 mt-2">{$t('project.noProjects')}</p>
    {/if}
  </div>

  <!-- User -->
  <div class="border-t border-slate-100 dark:border-slate-700 p-3 relative" data-user-menu>
    {#if $authStore.user}
      {@const user = $authStore.user}

      <!-- Popup menu -->
      {#if showUserMenu}
        <div class="absolute bottom-full left-3 right-3 mb-1 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-xl shadow-lg overflow-hidden z-50">
          <button
            onclick={openEditName}
            class="w-full flex items-center gap-3 px-4 py-3 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
          >
            <span class="text-base">✏️</span>
            <span>{$t('sidebar.changeNickname')}</span>
          </button>
          <div class="h-px bg-slate-100 dark:bg-slate-700"></div>
          <button
            onclick={() => { themeStore.toggle(); }}
            class="w-full flex items-center gap-3 px-4 py-3 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
          >
            <span class="text-base">{isDark ? '☀️' : '🌙'}</span>
            <span>{isDark ? $t('sidebar.lightMode') : $t('sidebar.darkMode')}</span>
          </button>
          <div class="h-px bg-slate-100 dark:bg-slate-700"></div>
          <button
            onclick={() => { localeStore.set(isKo ? 'en' : 'ko'); }}
            class="w-full flex items-center gap-3 px-4 py-3 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
          >
            <span class="text-base">🌐</span>
            <span>{isKo ? 'English' : '한국어'}</span>
          </button>
          <div class="h-px bg-slate-100 dark:bg-slate-700"></div>
          <button
            onclick={handleLogout}
            class="w-full flex items-center gap-3 px-4 py-3 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
          >
            <span class="text-base">↩</span>
            <span>{$t('sidebar.logout')}</span>
          </button>
        </div>
      {/if}

      <!-- 닉네임 편집 인라인 -->
      {#if editingName}
        <div class="flex items-center gap-2 mb-1">
          <input
            autofocus
            bind:value={nameInput}
            onkeydown={(e) => { if (e.key === 'Enter') saveEditName(); if (e.key === 'Escape') editingName = false; }}
            class="flex-1 text-sm px-2.5 py-1.5 border border-brand-500 rounded-lg bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 focus:outline-none"
            placeholder={$t('sidebar.nicknamePlaceholder')}
          />
          <button
            onclick={saveEditName}
            disabled={savingName || !nameInput.trim()}
            class="text-xs px-2.5 py-1.5 bg-brand-500 hover:bg-brand-600 text-white rounded-lg disabled:opacity-50 transition-colors shrink-0"
          >{savingName ? '...' : $t('common.save')}</button>
          <button
            onclick={() => (editingName = false)}
            class="text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
          >✕</button>
        </div>
      {/if}

      <!-- User row (click to open menu) -->
      <button
        onclick={(e) => { e.stopPropagation(); showUserMenu = !showUserMenu; }}
        class="w-full flex items-center gap-2 px-2 py-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors text-left"
      >
        {#if user.avatar_url}
          <img src={user.avatar_url} class="w-7 h-7 rounded-full shrink-0" alt={user.name} />
        {:else}
          <div class="w-7 h-7 rounded-full bg-brand-500 text-white text-xs flex items-center justify-center font-medium shrink-0">
            {user.name[0]}
          </div>
        {/if}
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-slate-700 dark:text-slate-200 truncate">{user.name}</p>
          <p class="text-xs text-slate-400 dark:text-slate-500 truncate">{user.email}</p>
        </div>
        <span class="text-slate-400 dark:text-slate-500 text-xs">⋯</span>
      </button>
    {/if}
  </div>
</aside>

{#if showCreate}
  <CreateProjectModal onClose={() => (showCreate = false)} />
{/if}
