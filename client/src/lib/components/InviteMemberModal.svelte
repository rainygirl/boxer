<script lang="ts">
  import { projectsApi } from '$lib/api/projects';
  import { authStore } from '$lib/stores/auth';
  import { t } from '$lib/i18n';
  import { get } from 'svelte/store';
  import { invalidate } from '$app/navigation';
  import type { Project } from '$lib/types';

  const {
    projects,
    onClose,
  }: {
    projects: Project[];
    onClose: () => void;
  } = $props();

  // Only show projects where the current user is owner
  const ownedProjects = $derived.by(() => {
    const userId = $authStore.user?.id;
    if (!userId) return projects;
    return projects.filter((p) =>
      p.members.some((m) => m.user.id === userId && m.role === 'owner')
    );
  });

  let selectedProjectId = $state(ownedProjects[0]?.id ?? '');
  let inviteEmail = $state('');
  let inviting = $state(false);
  let error = $state('');
  let success = $state(false);

  async function handleInvite(e: SubmitEvent) {
    e.preventDefault();
    if (!inviteEmail.trim() || !selectedProjectId) return;
    inviting = true;
    error = '';
    success = false;
    try {
      await projectsApi.inviteMember(selectedProjectId, inviteEmail.trim());
      inviteEmail = '';
      success = true;
      await invalidate('app:projects');
    } catch (err: any) {
      const msg = err?.response?.data?.detail;
      if (msg === 'No user found with that email') error = get(t)('member.notFound');
      else if (msg === 'User is already a member') error = get(t)('member.alreadyMember');
      else error = get(t)('member.inviteFailed');
    } finally {
      inviting = false;
    }
  }
</script>

<svelte:window onkeydown={(e) => e.key === 'Escape' && onClose()} />

<div class="fixed inset-0 z-50 flex items-center justify-center">
  <div class="absolute inset-0 bg-black/60" onclick={onClose}></div>
  <div class="relative bg-white dark:bg-slate-900 rounded-2xl shadow-2xl w-full max-w-sm mx-4 overflow-hidden">
    <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100 dark:border-slate-700">
      <h2 class="text-base font-semibold text-slate-800 dark:text-slate-100">{$t('member.inviteByEmail')}</h2>
      <button onclick={onClose} class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors">
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <div class="p-6 space-y-4">
      {#if ownedProjects.length === 0}
        <p class="text-sm text-slate-400 dark:text-slate-500 text-center py-4">{$t('member.noOwnedProjects')}</p>
      {:else}
        {#if ownedProjects.length > 1}
          <div>
            <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">{$t('sidebar.projects')}</label>
            <select
              bind:value={selectedProjectId}
              class="w-full text-sm px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              {#each ownedProjects as p (p.id)}
                <option value={p.id}>{p.name}</option>
              {/each}
            </select>
          </div>
        {:else}
          <p class="text-sm text-slate-600 dark:text-slate-400">
            <span class="font-medium text-slate-800 dark:text-slate-200">{ownedProjects[0].name}</span>
          </p>
        {/if}

        <form onsubmit={handleInvite} class="flex gap-2">
          <input
            type="email"
            bind:value={inviteEmail}
            placeholder={$t('member.emailPlaceholder')}
            class="flex-1 text-sm px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
          />
          <button
            type="submit"
            disabled={!inviteEmail.trim() || !selectedProjectId || inviting}
            class="px-3 py-2 text-sm font-medium bg-brand-500 hover:bg-brand-600 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            {inviting ? '...' : $t('member.invite')}
          </button>
        </form>
        {#if error}
          <p class="text-xs text-red-500">{error}</p>
        {/if}
        {#if success}
          <p class="text-xs text-green-600 dark:text-green-400">{$t('member.inviteSuccess')}</p>
        {/if}
      {/if}
    </div>
  </div>
</div>
