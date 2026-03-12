<script lang="ts">
  import { toastStore } from '$lib/stores/toast';
</script>

<div class="fixed bottom-5 right-5 z-[999] flex flex-col gap-2 pointer-events-none">
  {#each $toastStore as toast (toast.id)}
    <div
      class="pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg text-sm font-medium max-w-sm animate-slide-up
        {toast.type === 'error'
          ? 'bg-red-500 text-white'
          : toast.type === 'success'
            ? 'bg-green-500 text-white'
            : 'bg-slate-800 dark:bg-slate-100 text-white dark:text-slate-900'}"
    >
      <span class="flex-1">{toast.message}</span>
      <button
        onclick={() => toastStore.remove(toast.id)}
        class="opacity-60 hover:opacity-100 transition-opacity text-xs shrink-0"
      >✕</button>
    </div>
  {/each}
</div>

<style>
  @keyframes slide-up {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .animate-slide-up {
    animation: slide-up 0.2s ease-out;
  }
</style>
