<script lang="ts">
  import { t } from '$lib/i18n';
  import { sidebarOpen } from '$lib/stores/sidebar';
  import InviteMemberModal from '$lib/components/InviteMemberModal.svelte';
  import type { Project } from '$lib/types';

  const { data } = $props();
  const projects: Project[] = data.projects;
  let showInvite = $state(false);

  // Deduplicated member list
  const allMembers = (() => {
    const seen = new Set<number>();
    const list: { id: number; name: string; email: string; avatar_url: string | null }[] = [];
    for (const p of projects) {
      for (const m of p.members) {
        if (!seen.has(m.user.id)) {
          seen.add(m.user.id);
          list.push(m.user as any);
        }
      }
    }
    return list.sort((a, b) => a.name.localeCompare(b.name));
  })();
</script>

<div class="flex flex-col h-full overflow-hidden bg-white dark:bg-slate-900">
  <!-- Header -->
  <div class="flex items-center gap-3 px-3 md:px-6 h-[60px] border-b border-slate-200 dark:border-slate-700 shrink-0">
    <button
      class="md:hidden p-1.5 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
      onclick={() => sidebarOpen.update((v) => !v)}
    >
      <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
      </svg>
    </button>
    <h1 class="text-base font-semibold text-slate-800 dark:text-slate-100">{$t('sidebar.members')}</h1>
    <span class="text-xs text-slate-400 dark:text-slate-500">{allMembers.length}</span>
    <div class="flex-1"></div>
    <button
      onclick={() => (showInvite = true)}
      class="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium bg-brand-500 hover:bg-brand-600 text-white rounded-lg transition-colors"
    >
      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
      </svg>
      {$t('member.invite')}
    </button>
  </div>

  <!-- Member grid -->
  <div class="flex-1 overflow-y-auto p-4 md:p-6">
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
      {#each allMembers as m (m.id)}
        <a
          href="/app/member-issues/{m.id}"
          class="flex flex-col items-center gap-2 p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-brand-300 dark:hover:border-brand-600 hover:shadow-sm transition-all text-center"
        >
          {#if m.avatar_url}
            <img src={m.avatar_url} alt={m.name} class="w-12 h-12 rounded-full object-cover" />
          {:else}
            <div class="w-12 h-12 rounded-full bg-brand-500 text-white text-lg font-medium flex items-center justify-center">
              {m.name[0]}
            </div>
          {/if}
          <div class="min-w-0 w-full">
            <p class="text-sm font-medium text-slate-700 dark:text-slate-200 truncate">{m.name}</p>
            {#if (m as any).job_title}
              <p class="text-xs font-medium text-brand-500 dark:text-brand-400 truncate">{(m as any).job_title}</p>
            {/if}
            <p class="text-xs text-slate-400 dark:text-slate-500 truncate">{m.email}</p>
          </div>
        </a>
      {/each}
    </div>

    {#if allMembers.length === 0}
      <p class="text-sm text-slate-400 dark:text-slate-500 text-center mt-16">{$t('member.loading')}</p>
    {/if}
  </div>
</div>

{#if showInvite}
  <InviteMemberModal {projects} onClose={() => (showInvite = false)} />
{/if}
