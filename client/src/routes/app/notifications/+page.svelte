<script lang="ts">
  import { goto } from '$app/navigation';
  import { get } from 'svelte/store';
  import { notificationsApi } from '$lib/api/notifications';
  import { t } from '$lib/i18n';
  import { sidebarOpen } from '$lib/stores/sidebar';
  import { authStore } from '$lib/stores/auth';
  import { josa } from '$lib/utils/hangul';
  import type { Notification } from '$lib/types';

  let notifications = $state<Notification[]>([]);
  let loading = $state(true);

  const unreadCount = $derived(notifications.filter((n) => !n.read).length);

  async function load() {
    try {
      notifications = await notificationsApi.list();
    } catch {} finally {
      loading = false;
    }
  }

  $effect(() => {
    load();
    const interval = setInterval(load, 30000);
    return () => clearInterval(interval);
  });

  async function handleClick(n: Notification) {
    if (!n.read) {
      await notificationsApi.markRead(n.id);
      notifications = notifications.map((x) => x.id === n.id ? { ...x, read: true } : x);
    }
    if (n.project_id && n.task_id) {
      goto(`/app/project/${n.project_id}/issue/${n.task_id}`);
    }
  }

  async function markAllRead() {
    await notificationsApi.markAllRead();
    notifications = notifications.map((n) => ({ ...n, read: true }));
  }

  function relativeTime(dateStr: string): string {
    const tr = get(t);
    const diff = Date.now() - new Date(dateStr).getTime();
    const s = Math.floor(diff / 1000);
    if (s < 60) return (tr as any)('time.justNow') || 'just now';
    const m = Math.floor(s / 60);
    if (m < 60) return `${m}${tr('time.minutes')}`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h}${tr('time.hours')}`;
    return `${Math.floor(h / 24)}${tr('time.days')}`;
  }

  function notifText(n: Notification): string {
    const tr = get(t);
    const actor = n.actor?.name ?? tr('notification.someone');
    const ref = n.task_ref ?? tr('notification.anIssue');
    const name = $authStore.user?.name ?? '';
    const recipient_eul = name + josa(name, '을/를');
    if (n.type === 'mention') return tr('notification.mention', { actor, ref, recipient_eul });
    if (n.type === 'assigned') return tr('notification.assigned', { actor, ref, recipient_eul });
    return '';
  }
</script>

<div class="flex flex-col h-full overflow-hidden bg-white dark:bg-slate-900">
  <!-- Header -->
  <div class="flex items-center justify-between px-3 md:px-6 h-[60px] border-b border-slate-200 dark:border-slate-700 shrink-0">
    <div class="flex items-center gap-3">
      <button
        class="md:hidden p-1.5 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
        onclick={() => sidebarOpen.update((v) => !v)}
      >
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
      <h1 class="text-base font-semibold text-slate-800 dark:text-slate-100">{$t('notification.title')}</h1>
      {#if unreadCount > 0}
        <span class="px-2 py-0.5 bg-red-500 text-white text-xs font-bold rounded-full">{unreadCount}</span>
      {/if}
    </div>
    {#if unreadCount > 0}
      <button
        onclick={markAllRead}
        class="text-xs text-brand-500 hover:text-brand-600 dark:text-brand-400 dark:hover:text-brand-300 transition-colors"
      >{$t('notification.markAllRead')}</button>
    {/if}
  </div>

  <!-- List -->
  <div class="flex-1 overflow-y-auto">
    {#if loading}
      <div class="flex items-center justify-center py-20">
        <span class="w-2 h-2 rounded-full bg-brand-400 animate-pulse"></span>
      </div>
    {:else if notifications.length === 0}
      <div class="flex flex-col items-center justify-center py-20 text-slate-400 dark:text-slate-600">
        <svg class="w-10 h-10 mb-3 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0"/>
        </svg>
        <p class="text-sm">{$t('notification.empty')}</p>
      </div>
    {:else}
      <ul class="divide-y divide-slate-100 dark:divide-slate-800">
        {#each notifications as n (n.id)}
          <li>
            <button
              onclick={() => handleClick(n)}
              class="w-full flex items-start gap-3 px-4 md:px-6 py-4 text-left transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/60 {n.read ? '' : 'bg-blue-50/50 dark:bg-blue-900/10'}"
            >
              <!-- Actor avatar -->
              <div class="w-8 h-8 rounded-full shrink-0 overflow-hidden bg-brand-500 flex items-center justify-center text-xs font-bold text-white mt-0.5">
                {#if n.actor?.avatar_url}
                  <img src={n.actor.avatar_url} alt={n.actor.name} class="w-full h-full object-cover" />
                {:else}
                  {n.actor?.name?.[0]?.toUpperCase() ?? '?'}
                {/if}
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">{notifText(n)}</p>
                {#if n.task_title}
                  <p class="text-xs text-slate-400 dark:text-slate-500 truncate mt-0.5">{n.task_title}</p>
                {/if}
                <p class="text-xs text-slate-400 dark:text-slate-500 mt-1">{relativeTime(n.created_at)}</p>
              </div>
              {#if !n.read}
                <span class="w-2 h-2 rounded-full bg-blue-500 shrink-0 mt-2"></span>
              {/if}
            </button>
          </li>
        {/each}
      </ul>
    {/if}
  </div>
</div>
