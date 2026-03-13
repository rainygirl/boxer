<script lang="ts">
  import { authStore } from '$lib/stores/auth';
  import { authApi } from '$lib/api/auth';
  import { t } from '$lib/i18n';

  const { onClose }: { onClose: () => void } = $props();

  let nameInput = $state($authStore.user?.name ?? '');
  let saving = $state(false);
  let inputEl = $state<HTMLInputElement | null>(null);

  $effect(() => {
    setTimeout(() => inputEl?.focus(), 0);
  });

  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    if (!nameInput.trim() || saving) return;
    saving = true;
    try {
      const updated = await authApi.updateProfile(nameInput.trim());
      authStore.setUser(updated);
      onClose();
    } finally {
      saving = false;
    }
  }
</script>

<svelte:window onkeydown={(e) => e.key === 'Escape' && onClose()} />

<div class="fixed inset-0 z-50 flex items-center justify-center">
  <div class="absolute inset-0 bg-black/60" onclick={onClose}></div>
  <div class="relative bg-white dark:bg-slate-900 rounded-2xl shadow-2xl w-full max-w-sm mx-4">
    <form onsubmit={handleSubmit}>
      <div class="flex items-center justify-between px-6 pt-5 pb-0">
        <h2 class="text-base font-semibold text-slate-800 dark:text-slate-100">{$t('sidebar.changeNickname')}</h2>
        <button type="button" onclick={onClose} class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 w-7 h-7 flex items-center justify-center rounded hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">✕</button>
      </div>
      <div class="p-6">
        <input
          bind:this={inputEl}
          type="text"
          bind:value={nameInput}
          placeholder={$t('sidebar.nicknamePlaceholder')}
          class="w-full text-sm px-3 py-2.5 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
        />
      </div>
      <div class="flex items-center justify-end gap-2 px-6 py-4 bg-slate-50 dark:bg-slate-800/50 border-t border-slate-100 dark:border-slate-700 rounded-b-2xl">
        <button
          type="button"
          onclick={onClose}
          class="px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
        >{$t('common.cancel')}</button>
        <button
          type="submit"
          disabled={!nameInput.trim() || saving}
          class="px-4 py-2 text-sm font-medium bg-brand-500 hover:bg-brand-600 text-white rounded-lg transition-colors disabled:opacity-50"
        >{saving ? $t('common.saving') : $t('common.save')}</button>
      </div>
    </form>
  </div>
</div>
