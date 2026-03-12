<script lang="ts">
  import { projectsApi } from '$lib/api/projects';
  import type { ProjectMember } from '$lib/types';
  import { t } from '$lib/i18n';
  import { get } from 'svelte/store';

  const {
    projectId,
    isOwner,
    onClose,
  }: {
    projectId: string;
    isOwner: boolean;
    onClose: () => void;
  } = $props();

  let members = $state<ProjectMember[]>([]);
  let loading = $state(true);
  let inviteEmail = $state('');
  let inviting = $state(false);
  let error = $state('');

  async function loadMembers() {
    loading = true;
    try {
      members = await projectsApi.listMembers(projectId);
    } finally {
      loading = false;
    }
  }

  async function handleInvite(e: SubmitEvent) {
    e.preventDefault();
    if (!inviteEmail.trim()) return;
    inviting = true;
    error = '';
    try {
      const newMember = await projectsApi.inviteMember(projectId, inviteEmail.trim());
      members = [...members, newMember];
      inviteEmail = '';
    } catch (err: any) {
      const msg = err?.response?.data?.detail;
      if (msg === 'No user found with that email') error = get(t)('member.notFound');
      else if (msg === 'User is already a member') error = get(t)('member.alreadyMember');
      else error = get(t)('member.inviteFailed');
    } finally {
      inviting = false;
    }
  }

  async function handleRoleChange(member: ProjectMember, newRole: string) {
    try {
      const updated = await projectsApi.updateMemberRole(projectId, member.user.id, newRole);
      members = members.map((m) => (m.user.id === member.user.id ? updated : m));
    } catch {
      // ignore
    }
  }

  async function handleRemove(member: ProjectMember) {
    if (!confirm(get(t)('member.removeConfirm', { name: member.user.name || member.user.email }))) return;
    try {
      await projectsApi.removeMember(projectId, member.user.id);
      members = members.filter((m) => m.user.id !== member.user.id);
    } catch {
      // ignore
    }
  }

  $effect(() => {
    loadMembers();
  });
</script>

<svelte:window onkeydown={(e) => e.key === 'Escape' && onClose()} />

<div class="fixed inset-0 z-50 flex items-center justify-center">
  <div class="absolute inset-0 bg-black/30" onclick={onClose}></div>
  <div class="relative bg-white dark:bg-slate-900 rounded-2xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
    <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100 dark:border-slate-700">
      <h2 class="text-base font-semibold text-slate-800 dark:text-slate-100">{$t('member.manage')}</h2>
      <button onclick={onClose} class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors">
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <div class="p-6 space-y-5">
      <!-- Member list -->
      <div>
        {#if loading}
          <p class="text-sm text-slate-400 dark:text-slate-500 text-center py-4">{$t('member.loading')}</p>
        {:else}
          <ul class="space-y-2">
            {#each members as member (member.user.id)}
              <li class="flex items-center gap-3">
                {#if member.user.avatar_url}
                  <img src={member.user.avatar_url} alt={member.user.name} class="w-8 h-8 rounded-full object-cover" />
                {:else}
                  <div class="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-sm font-medium text-slate-600 dark:text-slate-300">
                    {(member.user.name || member.user.email).charAt(0).toUpperCase()}
                  </div>
                {/if}

                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-slate-800 dark:text-slate-100 truncate">{member.user.name || member.user.email}</p>
                  {#if member.user.name}
                    <p class="text-xs text-slate-400 dark:text-slate-500 truncate">{member.user.email}</p>
                  {/if}
                </div>

                {#if member.role === 'owner'}
                  <span class="text-xs font-medium text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-500/10 px-2 py-0.5 rounded-full">Owner</span>
                {:else if isOwner}
                  <select
                    value={member.role}
                    onchange={(e) => handleRoleChange(member, (e.target as HTMLSelectElement).value)}
                    class="text-xs border border-slate-200 dark:border-slate-600 rounded-md px-2 py-1 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 focus:outline-none focus:ring-2 focus:ring-brand-500"
                  >
                    <option value="member">Member</option>
                    <option value="viewer">Viewer</option>
                  </select>
                  <button
                    onclick={() => handleRemove(member)}
                    class="text-slate-300 dark:text-slate-600 hover:text-red-500 transition-colors"
                  >
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                {:else}
                  <span class="text-xs text-slate-400 dark:text-slate-500">{member.role === 'viewer' ? 'Viewer' : 'Member'}</span>
                {/if}
              </li>
            {/each}
          </ul>
        {/if}
      </div>

      {#if isOwner}
        <div class="border-t border-slate-100 dark:border-slate-700 pt-4">
          <p class="text-xs font-medium text-slate-500 dark:text-slate-400 mb-2">{$t('member.inviteByEmail')}</p>
          <form onsubmit={handleInvite} class="flex gap-2">
            <input
              type="email"
              bind:value={inviteEmail}
              placeholder={$t('member.emailPlaceholder')}
              class="flex-1 text-sm px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
            />
            <button
              type="submit"
              disabled={!inviteEmail.trim() || inviting}
              class="px-3 py-2 text-sm font-medium bg-brand-500 hover:bg-brand-600 text-white rounded-lg transition-colors disabled:opacity-50"
            >
              {inviting ? '...' : $t('member.invite')}
            </button>
          </form>
          {#if error}
            <p class="text-xs text-red-500 mt-1">{error}</p>
          {/if}
        </div>
      {/if}
    </div>
  </div>
</div>
