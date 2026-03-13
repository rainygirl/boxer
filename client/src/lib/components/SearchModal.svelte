<script lang="ts">
  import { goto } from '$app/navigation';
  import { tasksApi } from '$lib/api/tasks';
  import { TASK_STATUSES } from '$lib/types';
  import type { TaskSearchResult } from '$lib/types';

  const { onClose }: { onClose: () => void } = $props();

  let query = $state('');
  let results = $state<TaskSearchResult[]>([]);
  let loading = $state(false);
  let activeIndex = $state(0);
  let inputEl = $state<HTMLInputElement | null>(null);
  let debounceTimer: ReturnType<typeof setTimeout> | null = null;

  $effect(() => {
    setTimeout(() => inputEl?.focus(), 0);
  });

  function onInput() {
    activeIndex = 0;
    if (debounceTimer) clearTimeout(debounceTimer);
    const q = query.trim();
    if (!q) { results = []; loading = false; return; }
    loading = true;
    debounceTimer = setTimeout(async () => {
      try {
        results = await tasksApi.search(q);
      } finally {
        loading = false;
      }
    }, 200);
  }

  function selectResult(r: TaskSearchResult) {
    goto(`/app/project/${r.project_id}/issue/${r.id}`);
    onClose();
  }

  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') { onClose(); return; }
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      activeIndex = Math.min(activeIndex + 1, results.length - 1);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      activeIndex = Math.max(activeIndex - 1, 0);
    } else if (e.key === 'Enter') {
      if (results[activeIndex]) selectResult(results[activeIndex]);
    }
  }

  function getStatusCfg(status: string) {
    return TASK_STATUSES.find((s) => s.value === status) ?? TASK_STATUSES[0];
  }
</script>

<svelte:window onkeydown={(e) => { if (e.key === 'Escape') onClose(); }} />

<div
  class="fixed inset-0 z-[200] flex items-start justify-center pt-[15vh] bg-black/50"
  onclick={onClose}
>
  <div
    class="w-full max-w-xl bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-700 overflow-hidden"
    onclick={(e) => e.stopPropagation()}
  >
    <!-- Search input -->
    <div class="flex items-center gap-3 px-4 py-3 border-b border-slate-200 dark:border-slate-700">
      <svg class="w-4 h-4 text-slate-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35m0 0A7.5 7.5 0 1 0 6.5 6.5a7.5 7.5 0 0 0 10.15 10.15Z"/>
      </svg>
      <input
        bind:this={inputEl}
        bind:value={query}
        oninput={onInput}
        onkeydown={onKeydown}
        placeholder="Search issues..."
        class="flex-1 bg-transparent text-slate-800 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none text-sm"
      />
      {#if loading}
        <svg class="w-4 h-4 text-slate-400 animate-spin shrink-0" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
        </svg>
      {/if}
      <kbd class="hidden sm:inline-flex items-center gap-1 px-1.5 py-0.5 rounded border border-slate-200 dark:border-slate-600 text-[10px] text-slate-400">Esc</kbd>
    </div>

    <!-- Results -->
    {#if results.length > 0}
      <ul class="max-h-80 overflow-y-auto py-1">
        {#each results as r, i (r.id)}
          {@const sc = getStatusCfg(r.status)}
          <li>
            <button
              class="w-full flex items-center gap-3 px-4 py-2.5 text-left transition-colors {i === activeIndex ? 'bg-slate-100 dark:bg-slate-800' : 'hover:bg-slate-50 dark:hover:bg-slate-800/60'}"
              onclick={() => selectResult(r)}
              onmouseenter={() => (activeIndex = i)}
            >
              <!-- Project color dot -->
              <span class="w-2 h-2 rounded-full shrink-0" style="background:{r.project_color}"></span>
              <!-- Ref -->
              <span class="font-mono text-[11px] text-slate-400 dark:text-slate-500 shrink-0 w-16">{r.ref}</span>
              <!-- Title -->
              <span class="flex-1 text-sm text-slate-700 dark:text-slate-200 truncate">{r.title}</span>
              <!-- Status badge -->
              <span class="text-[10px] font-medium px-1.5 py-0.5 rounded-full shrink-0 {sc.color} {sc.bg}">{r.status.replace('_', ' ')}</span>
            </button>
          </li>
        {/each}
      </ul>
    {:else if query.trim() && !loading}
      <div class="px-4 py-6 text-center text-sm text-slate-400 dark:text-slate-500">No results for "{query}"</div>
    {:else if !query.trim()}
      <div class="px-4 py-4 text-xs text-slate-400 dark:text-slate-500">Type to search issues by title or ID</div>
    {/if}

    <!-- Footer hint -->
    <div class="flex items-center gap-4 px-4 py-2 border-t border-slate-100 dark:border-slate-800 text-[10px] text-slate-300 dark:text-slate-600">
      <span><kbd class="font-sans">↑↓</kbd> navigate</span>
      <span><kbd class="font-sans">↵</kbd> open</span>
      <span><kbd class="font-sans">Esc</kbd> close</span>
    </div>
  </div>
</div>
