<script lang="ts">
  import { page } from '$app/stores';
  import { matchKorean } from '$lib/utils/hangul';
  import type { User, ProjectMember } from '$lib/types';
  import { t } from '$lib/i18n';
  import { registerPopup, closeActivePopup } from '$lib/stores/popup';
  import { onMount } from 'svelte';

  const {
    value,
    onChange,
    initiallyOpen = false,
  }: {
    value: User | null;
    onChange: (user: User | null) => void;
    initiallyOpen?: boolean;
  } = $props();

  const projectId = $derived(($page.params as any).projectId as string);
  const members = $derived<ProjectMember[]>(
    (($page.data as any)?.projects ?? []).find((p: any) => p.id === projectId)?.members ?? []
  );

  let query = $state('');
  let open = $state(false);
  let activeIdx = $state(-1);
  let inputEl = $state<HTMLInputElement | null>(null);
  let listEl = $state<HTMLUListElement | null>(null);
  let blurTimer: ReturnType<typeof setTimeout> | null = null;

  const filtered = $derived(
    query.trim()
      ? members.filter((m) =>
          matchKorean(query, m.user.name) || m.user.email.toLowerCase().includes(query.toLowerCase())
        )
      : members
  );

  // 전체 항목: index 0 = null(담당자 없음), 1..n = filtered members
  const totalItems = $derived(1 + filtered.length);

  function select(user: User | null) {
    onChange(user);
    query = '';
    open = false;
    activeIdx = -1;
  }

  function openDropdown() {
    if (blurTimer) { clearTimeout(blurTimer); blurTimer = null; }
    if (open) {
      closeActivePopup();
      return;
    }
    open = true;
    activeIdx = -1;
    registerPopup(() => { open = false; activeIdx = -1; });
    setTimeout(() => inputEl?.focus(), 0);
  }

  onMount(() => { if (initiallyOpen) openDropdown(); });

  function handleBlur() {
    blurTimer = setTimeout(() => { open = false; activeIdx = -1; }, 150);
  }

  function handleKeydown(e: KeyboardEvent) {
    if (!open) return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      activeIdx = Math.min(activeIdx + 1, totalItems - 1);
      scrollActiveIntoView();
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      activeIdx = Math.max(activeIdx - 1, 0);
      scrollActiveIntoView();
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (activeIdx === 0) select(null);
      else if (activeIdx > 0) select(filtered[activeIdx - 1].user);
    } else if (e.key === 'Escape') {
      open = false;
      activeIdx = -1;
    }
  }

  function scrollActiveIntoView() {
    setTimeout(() => {
      const item = listEl?.querySelector(`[data-idx="${activeIdx}"]`);
      item?.scrollIntoView({ block: 'nearest' });
    }, 0);
  }

  $effect(() => {
    query;
    activeIdx = -1;
  });

  const displayName = $derived(value ? (value.name || value.email) : '');
</script>

<div class="relative">
  <div
    class="flex items-center gap-2 px-2.5 py-1.5 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 cursor-pointer"
    onclick={(e) => { e.stopPropagation(); openDropdown(); }}
  >
    {#if value}
      {#if value.avatar_url}
        <img src={value.avatar_url} class="w-5 h-5 rounded-full shrink-0" alt="" />
      {:else}
        <div class="w-5 h-5 rounded-full bg-brand-400 text-white text-[10px] flex items-center justify-center shrink-0">
          {(value.name || value.email)[0]}
        </div>
      {/if}
      <span class="text-sm text-slate-700 dark:text-slate-200 flex-1 truncate">{displayName}</span>
      <button
        onclick={(e) => { e.stopPropagation(); select(null); }}
        class="text-slate-300 dark:text-slate-600 hover:text-slate-500 text-xs"
      >✕</button>
    {:else}
      <span class="text-sm text-slate-400 dark:text-slate-500 flex-1">{$t('assignee.none')}</span>
      <svg class="w-3.5 h-3.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    {/if}
  </div>

  {#if open}
    <div class="absolute z-50 top-full left-0 right-0 mt-1 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-xl shadow-lg overflow-hidden">
      <div class="p-2 border-b border-slate-100 dark:border-slate-700">
        <input
          bind:this={inputEl}
          bind:value={query}
          onblur={handleBlur}
          onkeydown={handleKeydown}
          placeholder={$t('assignee.search')}
          class="w-full text-sm px-2 py-1 bg-slate-50 dark:bg-slate-700 text-slate-800 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 rounded-lg border-0 focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
      </div>
      <ul bind:this={listEl} class="max-h-48 overflow-y-auto scrollbar-thin py-1">
        <li>
          <button
            data-idx="0"
            onmousedown={() => select(null)}
            class="w-full flex items-center gap-2.5 px-3 py-2 text-sm transition-colors {activeIdx === 0 ? 'bg-brand-500 text-white' : 'text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700'}"
          >
            <div class="w-6 h-6 rounded-full bg-slate-200 dark:bg-slate-600 flex items-center justify-center text-slate-400 text-xs">-</div>
            <span>{$t('assignee.none')}</span>
          </button>
        </li>
        {#each filtered as m, i (m.user.id)}
          <li>
            <button
              data-idx={i + 1}
              onmousedown={() => select(m.user)}
              class="w-full flex items-center gap-2.5 px-3 py-2 text-sm transition-colors {activeIdx === i + 1 ? 'bg-brand-500 text-white' : 'hover:bg-slate-50 dark:hover:bg-slate-700'}"
            >
              {#if m.user.avatar_url}
                <img src={m.user.avatar_url} class="w-6 h-6 rounded-full" alt="" />
              {:else}
                <div class="w-6 h-6 rounded-full bg-brand-400 text-white text-[10px] flex items-center justify-center">
                  {(m.user.name || m.user.email)[0]}
                </div>
              {/if}
              <div class="flex-1 min-w-0 text-left">
                <p class="font-medium truncate {activeIdx === i + 1 ? 'text-white' : 'text-slate-700 dark:text-slate-200'}">{m.user.name || m.user.email}</p>
                {#if m.user.name}
                  <p class="text-xs truncate {activeIdx === i + 1 ? 'text-brand-100' : 'text-slate-400 dark:text-slate-500'}">{m.user.email}</p>
                {/if}
              </div>
            </button>
          </li>
        {/each}
        {#if filtered.length === 0}
          <li class="px-3 py-3 text-sm text-slate-400 dark:text-slate-500 text-center">{$t('assignee.noResults')}</li>
        {/if}
      </ul>
    </div>
  {/if}
</div>
