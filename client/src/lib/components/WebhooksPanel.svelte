<script lang="ts">
  import { integrationsApi, WEBHOOK_EVENTS } from '$lib/api/integrations';
  import type { ProjectWebhook } from '$lib/api/integrations';
  import { t } from '$lib/i18n';

  const { projectId }: { projectId: string } = $props();

  let webhooks = $state<ProjectWebhook[]>([]);
  let showForm = $state(false);
  let editingId = $state<string | null>(null);

  // Form state
  let formUrl = $state('');
  let formSecret = $state('');
  let formEvents = $state<string[]>([]);
  let formActive = $state(true);
  let saving = $state(false);

  async function load() {
    webhooks = await integrationsApi.listWebhooks(projectId);
  }

  function openNew() {
    editingId = null;
    formUrl = '';
    formSecret = '';
    formEvents = [];
    formActive = true;
    showForm = true;
  }

  function openEdit(wh: ProjectWebhook) {
    editingId = wh.id;
    formUrl = wh.url;
    formSecret = wh.secret;
    formEvents = [...wh.events];
    formActive = wh.active;
    showForm = true;
  }

  function cancelForm() {
    showForm = false;
    editingId = null;
  }

  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    if (!formUrl.trim()) return;
    saving = true;
    try {
      if (editingId) {
        const updated = await integrationsApi.updateWebhook(projectId, editingId, {
          url: formUrl,
          secret: formSecret,
          events: formEvents,
          active: formActive,
        });
        webhooks = webhooks.map((w) => (w.id === editingId ? updated : w));
      } else {
        const created = await integrationsApi.createWebhook(projectId, {
          url: formUrl,
          secret: formSecret,
          events: formEvents,
          active: formActive,
        });
        webhooks = [...webhooks, created];
      }
      cancelForm();
    } finally {
      saving = false;
    }
  }

  async function toggleActive(wh: ProjectWebhook) {
    const updated = await integrationsApi.updateWebhook(projectId, wh.id, { active: !wh.active });
    webhooks = webhooks.map((w) => (w.id === wh.id ? updated : w));
  }

  async function handleDelete(wh: ProjectWebhook) {
    if (!confirm($t('integration.webhookDeleteConfirm'))) return;
    await integrationsApi.deleteWebhook(projectId, wh.id);
    webhooks = webhooks.filter((w) => w.id !== wh.id);
  }

  function toggleEvent(ev: string) {
    if (formEvents.includes(ev)) {
      formEvents = formEvents.filter((e) => e !== ev);
    } else {
      formEvents = [...formEvents, ev];
    }
  }

  $effect(() => { load(); });
</script>

<div class="space-y-4">
  <!-- Webhook list -->
  {#if webhooks.length > 0}
    <ul class="space-y-2">
      {#each webhooks as wh (wh.id)}
        <li class="flex items-center gap-3 p-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
          <!-- Active toggle -->
          <button
            type="button"
            onclick={() => toggleActive(wh)}
            class="shrink-0 w-8 h-4 rounded-full transition-colors relative {wh.active ? 'bg-brand-500' : 'bg-slate-300 dark:bg-slate-600'}"
            title={wh.active ? $t('integration.active') : $t('integration.inactive')}
          >
            <span class="absolute top-0.5 w-3 h-3 rounded-full bg-white shadow transition-transform {wh.active ? 'translate-x-4' : 'translate-x-0.5'}"></span>
          </button>

          <div class="flex-1 min-w-0">
            <p class="text-xs font-mono text-slate-700 dark:text-slate-200 truncate">{wh.url}</p>
            {#if wh.events.length > 0}
              <p class="text-[10px] text-slate-400 dark:text-slate-500 mt-0.5">{wh.events.join(', ')}</p>
            {:else}
              <p class="text-[10px] text-slate-400 dark:text-slate-500 mt-0.5">{$t('integration.allEvents')}</p>
            {/if}
          </div>

          <button
            type="button"
            onclick={() => openEdit(wh)}
            class="shrink-0 text-xs text-slate-400 hover:text-brand-500 dark:hover:text-brand-400 transition-colors"
          >{$t('common.edit')}</button>
          <button
            type="button"
            onclick={() => handleDelete(wh)}
            class="shrink-0 text-xs text-slate-400 hover:text-red-500 transition-colors"
          >✕</button>
        </li>
      {/each}
    </ul>
  {:else if !showForm}
    <p class="text-sm text-slate-400 dark:text-slate-500 text-center py-4">
      {$t('integration.noWebhooks')}
    </p>
  {/if}

  <!-- Add / Edit form -->
  {#if showForm}
    <form onsubmit={handleSubmit} class="space-y-3 border border-slate-200 dark:border-slate-700 rounded-lg p-4 bg-slate-50 dark:bg-slate-800/50">
      <p class="text-xs font-semibold text-slate-600 dark:text-slate-300">
        {editingId ? $t('integration.editWebhook') : $t('integration.addWebhook')}
      </p>

      <div>
        <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">
          {$t('integration.webhookUrl')} *
        </label>
        <input
          type="url"
          bind:value={formUrl}
          required
          placeholder="https://your-server.com/hook"
          class="w-full text-sm px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
      </div>

      <div>
        <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">
          {$t('integration.secret')} <span class="font-normal">{$t('integration.optional')}</span>
        </label>
        <input
          type="text"
          bind:value={formSecret}
          placeholder={$t('integration.secretPlaceholder')}
          class="w-full text-sm px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
      </div>

      <div>
        <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1.5">
          {$t('integration.events')} <span class="font-normal">{$t('integration.eventsHint')}</span>
        </label>
        <div class="flex flex-wrap gap-2">
          {#each WEBHOOK_EVENTS as ev}
            <button
              type="button"
              onclick={() => toggleEvent(ev)}
              class="px-2 py-0.5 text-[11px] rounded-full border transition-colors
                     {formEvents.includes(ev)
                       ? 'border-brand-500 bg-brand-50 dark:bg-brand-500/10 text-brand-600 dark:text-brand-400'
                       : 'border-slate-200 dark:border-slate-600 text-slate-500 dark:text-slate-400 hover:border-brand-300'}"
            >{ev}</button>
          {/each}
        </div>
      </div>

      <div class="flex items-center justify-between pt-1">
        <button
          type="button"
          onclick={cancelForm}
          class="text-sm text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
        >{$t('common.cancel')}</button>
        <button
          type="submit"
          disabled={!formUrl.trim() || saving}
          class="px-4 py-2 text-sm font-medium bg-brand-500 hover:bg-brand-600 text-white rounded-lg transition-colors disabled:opacity-50"
        >{saving ? '...' : $t('common.save')}</button>
      </div>
    </form>
  {:else}
    <button
      type="button"
      onclick={openNew}
      class="w-full flex items-center justify-center gap-1.5 px-3 py-2 text-sm text-slate-500 dark:text-slate-400 hover:text-brand-600 dark:hover:text-brand-400 border border-dashed border-slate-300 dark:border-slate-600 hover:border-brand-400 rounded-lg transition-colors"
    >
      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
      </svg>
      {$t('integration.addWebhook')}
    </button>
  {/if}
</div>
