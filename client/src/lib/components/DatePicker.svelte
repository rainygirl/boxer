<script lang="ts">
  import { dateLocale } from '$lib/i18n';

  const {
    value,
    onChange,
    placeholder = '',
    plain = false,              // plain=true: text-only style (for board/table cells)
    monthFormat = 'short' as 'short' | 'long',
  }: {
    value: string;
    onChange: (v: string) => void;
    placeholder?: string;
    plain?: boolean;
    monthFormat?: 'short' | 'long';
  } = $props();

  let inputEl = $state<HTMLInputElement | null>(null);

  const formatted = $derived.by(() => {
    if (!value) return '';
    const [y, m, d] = value.split('-').map(Number);
    const date = new Date(y, m - 1, d);
    return new Intl.DateTimeFormat($dateLocale, {
      month: monthFormat,
      day: 'numeric',
    }).format(date);
  });

  const isOverdue = $derived(
    !!value && new Date(value + 'T00:00:00') < new Date(new Date().toDateString())
  );

  function openPicker() {
    try { (inputEl as any)?.showPicker(); } catch {}
  }
</script>

{#if plain}
  <!-- Plain / inline mode: looks like text, triggers native picker on click -->
  <div class="relative inline-flex items-center">
    <button
      type="button"
      onclick={openPicker}
      class="flex items-center gap-0.5 text-[11px] rounded px-0.5 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors whitespace-nowrap
        {isOverdue
          ? 'text-red-400 dark:text-red-400'
          : value
            ? 'text-slate-400 dark:text-slate-500'
            : 'text-slate-300 dark:text-slate-600'}"
    >
      {#if value}
        ~{formatted}
      {:else}
        {placeholder || '—'}
      {/if}
    </button>

    <input
      bind:this={inputEl}
      type="date"
      value={value}
      onchange={(e) => onChange((e.currentTarget as HTMLInputElement).value)}
      tabindex="-1"
      class="absolute inset-0 opacity-0 pointer-events-none w-full h-full"
    />
  </div>
{:else}
  <!-- Default mode: full bordered input button -->
  <div class="relative flex items-center w-full">
    <button
      type="button"
      onclick={openPicker}
      class="flex items-center gap-2 w-full px-2.5 py-1.5 text-sm rounded-lg border bg-white dark:bg-slate-800 transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500 hover:border-slate-300 dark:hover:border-slate-500
        {isOverdue
          ? 'border-red-300 dark:border-red-700 text-red-500 dark:text-red-400'
          : value
            ? 'border-slate-200 dark:border-slate-600 text-slate-700 dark:text-slate-200'
            : 'border-slate-200 dark:border-slate-600 text-slate-400 dark:text-slate-500'}"
    >
      <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="4" width="18" height="18" rx="2"/>
        <path d="M16 2v4M8 2v4M3 10h18"/>
      </svg>
      <span class="flex-1 text-left">
        {formatted || placeholder}
      </span>
      {#if value}
        <span
          role="button"
          tabindex="0"
          onclick={(e) => { e.stopPropagation(); onChange(''); }}
          onkeydown={(e) => { if (e.key === 'Enter') { e.stopPropagation(); onChange(''); } }}
          class="text-slate-300 dark:text-slate-600 hover:text-slate-500 dark:hover:text-slate-400 text-xs leading-none px-0.5"
        >✕</span>
      {/if}
    </button>

    <input
      bind:this={inputEl}
      type="date"
      value={value}
      onchange={(e) => onChange((e.currentTarget as HTMLInputElement).value)}
      tabindex="-1"
      class="absolute inset-0 opacity-0 pointer-events-none w-full h-full cursor-pointer"
    />
  </div>
{/if}
