<script lang="ts">
  import { page } from '$app/stores';
  import { invalidate, goto } from '$app/navigation';
  import { authStore } from '$lib/stores/auth';
  import { themeStore } from '$lib/stores/theme';
  import { t } from '$lib/i18n';
  import { get } from 'svelte/store';
  import { projectsApi } from '$lib/api/projects';
  import { draggingTask, sidebarHoverProjectId } from '$lib/stores/drag';
  import { sidebarOpen } from '$lib/stores/sidebar';
  import { afterNavigate } from '$app/navigation';
  import type { Project } from '$lib/types';

  afterNavigate(() => sidebarOpen.set(false));
  import CreateProjectModal from './CreateProjectModal.svelte';
  import LanguageModal from './LanguageModal.svelte';
  import EditNicknameModal from './EditNicknameModal.svelte';
  import InviteMemberModal from './InviteMemberModal.svelte';
  import { tasksApi } from '$lib/api/tasks';
  import type { TaskSearchResult } from '$lib/types';

  const { projects }: { projects: Project[] } = $props();

  // ── Sidebar search ────────────────────────────────────────────────────────
  let searchQuery = $state('');
  let searchResults = $state<TaskSearchResult[]>([]);
  let searchLoading = $state(false);
  let searchSelectedIdx = $state(-1);
  let searchTimer: ReturnType<typeof setTimeout> | null = null;

  function onSearchInput() {
    if (searchTimer) clearTimeout(searchTimer);
    const q = searchQuery.trim();
    if (!q) { searchResults = []; searchLoading = false; searchSelectedIdx = -1; return; }
    // Keep old results visible (no clear) — only set loading flag
    searchLoading = true;
    searchTimer = setTimeout(async () => {
      try {
        const next = await tasksApi.search(q);
        searchResults = next;
        searchSelectedIdx = -1;
      } catch {
        searchResults = [];
      } finally {
        searchLoading = false;
      }
    }, 300);
  }

  function onSearchKeydown(e: KeyboardEvent) {
    if (!searchResults.length) return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      searchSelectedIdx = Math.min(searchSelectedIdx + 1, searchResults.length - 1);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      searchSelectedIdx = Math.max(searchSelectedIdx - 1, -1);
    } else if (e.key === 'Enter' && searchSelectedIdx >= 0) {
      e.preventDefault();
      goToResult(searchResults[searchSelectedIdx]);
    } else if (e.key === 'Escape') {
      clearSearch();
    }
  }

  function clearSearch() {
    searchQuery = '';
    searchResults = [];
    searchLoading = false;
    searchSelectedIdx = -1;
  }

  function goToResult(r: TaskSearchResult) {
    clearSearch();
    goto(`/app/project/${r.project_id}/issue/${r.id}`);
  }

  let showCreate = $state(false);
  let showLanguageModal = $state(false);
  let showNicknameModal = $state(false);
  let showInviteMember = $state(false);
  let showUserMenu = $state(false);

  const currentProjectId = $derived($page.params.projectId);
  const favorites = $derived(projects.filter((p) => p.is_favorite));

  // Deduplicated member list across all projects (by user id)
  const allMembers = $derived.by(() => {
    const seen = new Set<number>();
    const list: { id: number; name: string; avatar_url: string | null }[] = [];
    for (const p of projects) {
      for (const m of p.members) {
        if (!seen.has(m.user.id)) {
          seen.add(m.user.id);
          list.push(m.user);
        }
      }
    }
    return list;
  });
  const MEMBER_MAX = 20;
  const visibleMembers = $derived(allMembers.slice(0, MEMBER_MAX));
  const extraMembers = $derived(Math.max(0, allMembers.length - MEMBER_MAX));

  // Per-project expand/collapse state; auto-expand active project
  let expandedProjects = $state(new Set<string>(currentProjectId ? [currentProjectId] : []));

  $effect(() => {
    if (currentProjectId && !expandedProjects.has(currentProjectId)) {
      expandedProjects = new Set([...expandedProjects, currentProjectId]);
    }
  });

  function toggleExpand(id: string) {
    const next = new Set(expandedProjects);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    expandedProjects = next;
  }

  const themeLabel = $derived(
    $themeStore === 'light' ? { icon: '🌙', label: $t('sidebar.blueMode') } :
    $themeStore === 'blue'  ? { icon: '⬛', label: $t('sidebar.blackMode') } :
                              { icon: '☀️', label: $t('sidebar.lightMode') }
  );

  async function toggleFavorite(e: MouseEvent, p: Project) {
    e.preventDefault();
    e.stopPropagation();
    await projectsApi.toggleFavorite(p.id);
    await invalidate('app:projects');
  }

  function handleLogout() {
    authStore.logout();
    goto('/login');
  }

  function openEditName() {
    showUserMenu = false;
    showNicknameModal = true;
  }

  function closeMenu(e: MouseEvent) {
    const target = e.target as HTMLElement;
    if (!target.closest('[data-user-menu]')) {
      showUserMenu = false;
    }
  }

  // During a drag, track which project the cursor is over via pointermove + elementFromPoint.
  // onpointerenter/leave don't fire reliably when svelte-dnd-action holds pointer capture.
  $effect(() => {
    if (!$draggingTask) {
      sidebarHoverProjectId.set(null);
      return;
    }

    function onMove(e: PointerEvent) {
      // elementsFromPoint returns all layers top-to-bottom.
      // The svelte-dnd-action dragged clone (#dnd-action-dragged-el) sits on top
      // and would block elementFromPoint — skip it to reach the element below.
      const els = document.elementsFromPoint(e.clientX, e.clientY);
      const el = els.find(
        (el) => el.id !== 'dnd-action-dragged-el' && !el.closest('#dnd-action-dragged-el')
      );
      const id = el?.closest('[data-project-id]')?.getAttribute('data-project-id') ?? null;
      sidebarHoverProjectId.set(id);
    }

    document.addEventListener('pointermove', onMove);
    return () => {
      document.removeEventListener('pointermove', onMove);
      sidebarHoverProjectId.set(null);
    };
  });
</script>

<svelte:window onclick={closeMenu} />

<aside class="
  w-60 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-700
  flex flex-col h-full shrink-0
  fixed md:relative inset-y-0 left-0 z-40 md:z-auto
  transform transition-transform duration-200
  {$sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
">
  <!-- Logo -->
  <div class="px-4 h-[60px] flex items-center border-b border-slate-100 dark:border-slate-700">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <span class="text-xl">📦</span>
        <span class="font-bold text-slate-800 dark:text-slate-100 text-lg">Boxer</span>
      </div>
      <button
        class="md:hidden p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
        onclick={() => sidebarOpen.set(false)}
      >
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  </div>

  <!-- Search -->
  <div class="px-3 pt-3 pb-1 relative">
    <div class="relative">
      <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z"/>
      </svg>
      <input
        bind:value={searchQuery}
        oninput={onSearchInput}
        onkeydown={onSearchKeydown}
        placeholder={$t('myIssues.search')}
        class="w-full text-xs pl-8 pr-6 py-1.5 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500"
      />
      {#if searchLoading}
        <!-- Subtle pulse dot instead of replacing results -->
        <span class="absolute right-2.5 top-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-brand-400 animate-pulse pointer-events-none"></span>
      {:else if searchQuery}
        <button onclick={clearSearch} class="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs leading-none">✕</button>
      {/if}
    </div>

    {#if searchQuery.trim() && searchResults.length > 0}
      <div class="absolute left-3 right-3 top-full mt-1 z-50 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-xl shadow-xl overflow-hidden">
        <ul class="max-h-64 overflow-y-auto py-1">
          {#each searchResults as r, i (r.id)}
            <li>
              <button
                onclick={() => goToResult(r)}
                onmouseenter={() => (searchSelectedIdx = i)}
                class="w-full flex items-center gap-2 px-3 py-2 text-left transition-colors
                       {i === searchSelectedIdx
                         ? 'bg-brand-50 dark:bg-brand-500/10'
                         : 'hover:bg-slate-50 dark:hover:bg-slate-700'}"
              >
                <span class="text-[10px] font-mono text-slate-400 shrink-0">{r.ref}</span>
                <span class="text-xs text-slate-700 dark:text-slate-200 truncate flex-1">{r.title}</span>
              </button>
            </li>
          {/each}
        </ul>
      </div>
    {/if}
  </div>

  <!-- My Notifications + My Issues -->
  <div class="px-3 pt-1 pb-1 flex flex-col gap-0.5">
    <a
      href="/app/notifications"
      class="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors
             {$page.url.pathname === '/app/notifications'
               ? 'bg-brand-50 dark:bg-brand-500/10 text-brand-700 dark:text-brand-400 font-medium'
               : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-800 dark:hover:text-slate-200'}"
    >
      <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
      </svg>
      {$t('notification.title')}
    </a>
    <a
      href="/app/my-issues"
      class="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors
             {$page.url.pathname === '/app/my-issues'
               ? 'bg-brand-50 dark:bg-brand-500/10 text-brand-700 dark:text-brand-400 font-medium'
               : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-800 dark:hover:text-slate-200'}"
    >
      <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="8" r="4"/>
        <path stroke-linecap="round" d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
      </svg>
      {$t('sidebar.myIssues')}
    </a>
  </div>

  <!-- Projects -->
  <div class="flex-1 overflow-y-auto py-3 scrollbar-thin">

    <!-- 즐겨찾기 섹션 -->
    {#if favorites.length > 0}
      <div class="px-4 mb-1">
        <span class="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">{$t('sidebar.favorites')}</span>
      </div>
      <nav class="space-y-0.5 px-2 mb-3">
        {#each favorites as p (p.id)}
          {@const isActive = currentProjectId === p.id}
          {@const isDragTarget = $draggingTask !== null && $sidebarHoverProjectId === p.id && !isActive}
          <a
            href="/app/project/{p.id}"
            data-project-id={isActive ? null : p.id}
            class="flex items-center gap-2 px-2 py-1.5 rounded-lg text-sm transition-colors group {
              isDragTarget
                ? 'bg-brand-100 dark:bg-brand-500/20 ring-2 ring-brand-400 dark:ring-brand-500 text-brand-700 dark:text-brand-300'
                : isActive
                  ? 'bg-brand-50 dark:bg-brand-500/10 text-brand-700 dark:text-brand-400 font-medium'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800'
            }"
          >
            <svg class="w-3.5 h-3.5 shrink-0 text-yellow-400 fill-yellow-400" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5Z"/>
            </svg>
            <span class="flex-1 truncate">{p.name}</span>
            {#if isDragTarget}
              <span class="text-[10px] font-semibold text-brand-500 dark:text-brand-400 shrink-0">여기에 놓기</span>
            {/if}
          </a>
        {/each}
      </nav>
    {/if}

    <!-- 전체 프로젝트 섹션 -->
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
        {@const isActive = currentProjectId === p.id}
        {@const isDragTarget = $draggingTask !== null && $sidebarHoverProjectId === p.id && !isActive}
        {@const isExpanded = expandedProjects.has(p.id)}
        {@const isReports = isActive && $page.url.searchParams.get('s') === 'reports'}
        <div>
          <div class="flex items-center group">
            <!-- Expand/collapse toggle -->
            <button
              onclick={(e) => { e.preventDefault(); e.stopPropagation(); toggleExpand(p.id); }}
              class="shrink-0 w-5 h-8 flex items-center justify-center text-slate-300 dark:text-slate-600 hover:text-slate-500 dark:hover:text-slate-400 transition-colors"
              aria-label="toggle"
            >
              <svg class="w-2 h-2 transition-transform duration-150 {isExpanded ? 'rotate-90' : ''}" viewBox="0 0 6 10" fill="currentColor">
                <path d="M1 1l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
              </svg>
            </button>
            <a
              href="/app/project/{p.id}"
              data-project-id={isActive ? null : p.id}
              class="flex-1 flex items-center gap-2 px-1.5 py-2 rounded-lg text-sm transition-colors min-w-0 {
                isDragTarget
                  ? 'bg-brand-100 dark:bg-brand-500/20 ring-2 ring-brand-400 dark:ring-brand-500 text-brand-700 dark:text-brand-300'
                  : isActive
                    ? 'bg-brand-50 dark:bg-brand-500/10 text-brand-700 dark:text-brand-400 font-medium'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800'
              }"
            >
              <span class="w-2.5 h-2.5 rounded-full shrink-0 transition-transform {isDragTarget ? 'scale-125' : ''}" style="background-color: {p.color}"></span>
              <span class="flex-1 truncate">{p.name}</span>
              <!-- 별 즐겨찾기 버튼 (hover 시 표시, 즐겨찾기면 항상 표시) -->
              <button
                onclick={(e) => toggleFavorite(e, p)}
                class="shrink-0 transition-all {p.is_favorite ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}"
                title={p.is_favorite ? '즐겨찾기 해제' : '즐겨찾기'}
              >
                <svg class="w-3.5 h-3.5 transition-colors {p.is_favorite ? 'text-yellow-400 fill-yellow-400' : 'text-slate-300 dark:text-slate-600 fill-none hover:text-yellow-400'}" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5Z"/>
                </svg>
              </button>
              {#if isDragTarget}
                <span class="text-[10px] font-semibold text-brand-500 dark:text-brand-400 shrink-0">여기에 놓기</span>
              {/if}
            </a>
          </div>
          {#if isExpanded}
            <div data-project-id={isActive ? null : p.id} class="ml-5 pl-2 border-l border-slate-200 dark:border-slate-700 flex flex-col gap-0.5 mb-0.5">
              <a
                href="/app/project/{p.id}?s=issues"
                class="flex items-center gap-1.5 px-2 py-1 rounded-md text-xs transition-colors {isActive && !isReports
                  ? 'text-brand-600 dark:text-brand-400 font-medium'
                  : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'}"
              >
                <svg class="w-3 h-3 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                </svg>
                {$t('nav.issues')}
              </a>
              <a
                href="/app/project/{p.id}?s=reports"
                class="flex items-center gap-1.5 px-2 py-1 rounded-md text-xs transition-colors {isReports
                  ? 'text-brand-600 dark:text-brand-400 font-medium'
                  : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'}"
              >
                <svg class="w-3 h-3 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                </svg>
                {$t('nav.reports')}
              </a>
            </div>
          {/if}
        </div>
      {/each}
    </nav>

    {#if projects.length === 0}
      <p class="px-4 text-xs text-slate-400 dark:text-slate-500 mt-2">{$t('project.noProjects')}</p>
    {/if}

    <!-- Members — same hierarchy as Projects -->
    {#if visibleMembers.length > 0}
      <div class="mt-4">
        <div class="flex items-center justify-between px-4 mb-2">
          <a href="/app/members" class="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider hover:text-brand-600 dark:hover:text-brand-400 transition-colors">
            {$t('sidebar.members')}
          </a>
          <button
            onclick={() => (showInviteMember = true)}
            class="text-slate-400 hover:text-brand-600 dark:hover:text-brand-400 transition-colors text-lg leading-none"
            title={$t('member.invite')}
          >+</button>
        </div>
        <div class="flex flex-wrap gap-1 px-4">
          {#each visibleMembers as m (m.id)}
            <a href="/app/member-issues/{m.id}" title={m.name} class="shrink-0">
              {#if m.avatar_url}
                <img src={m.avatar_url} alt={m.name} class="w-7 h-7 rounded-full object-cover hover:ring-2 hover:ring-brand-400 transition-all" />
              {:else}
                <div class="w-7 h-7 rounded-full bg-brand-500 text-white text-xs flex items-center justify-center font-medium hover:ring-2 hover:ring-brand-400 transition-all">
                  {m.name[0]}
                </div>
              {/if}
            </a>
          {/each}
          {#if extraMembers > 0}
            <a href="/app/members" class="w-7 h-7 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400 text-[10px] font-semibold flex items-center justify-center hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors shrink-0">
              +{extraMembers}
            </a>
          {/if}
        </div>
      </div>
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
            <span class="text-base">{themeLabel.icon}</span>
            <span>{themeLabel.label}</span>
          </button>
          <div class="h-px bg-slate-100 dark:bg-slate-700"></div>
          <button
            onclick={() => { showUserMenu = false; showLanguageModal = true; }}
            class="w-full flex items-center gap-3 px-4 py-3 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
          >
            <span class="text-base">🌐</span>
            <span>{$t('sidebar.language')}</span>
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

{#if showLanguageModal}
  <LanguageModal onClose={() => (showLanguageModal = false)} />
{/if}

{#if showNicknameModal}
  <EditNicknameModal onClose={() => (showNicknameModal = false)} />
{/if}

{#if showInviteMember}
  <InviteMemberModal {projects} onClose={() => (showInviteMember = false)} />
{/if}
