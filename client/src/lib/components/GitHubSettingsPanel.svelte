<script lang="ts">
  import { integrationsApi } from '$lib/api/integrations';
  import type { GitHubIntegration } from '$lib/api/integrations';
  import { t } from '$lib/i18n';

  const { projectId }: { projectId: string } = $props();

  let integration = $state<GitHubIntegration | null>(null);
  let repoOwner = $state('');
  let repoName = $state('');
  let secret = $state('');
  let saving = $state(false);
  let saved = $state(false);
  let copied = $state(false);

  const webhookUrl = $derived(
    typeof window !== 'undefined'
      ? `${window.location.origin}/webhook/github/${projectId}/`
      : ''
  );

  async function load() {
    integration = await integrationsApi.getGitHub(projectId);
    repoOwner = integration.repo_owner;
    repoName = integration.repo_name;
    secret = integration.webhook_secret;
  }

  async function handleSave(e: SubmitEvent) {
    e.preventDefault();
    saving = true;
    saved = false;
    try {
      integration = await integrationsApi.updateGitHub(projectId, {
        repo_owner: repoOwner,
        repo_name: repoName,
        webhook_secret: secret,
      });
      saved = true;
      setTimeout(() => (saved = false), 2000);
    } finally {
      saving = false;
    }
  }

  async function copyUrl() {
    await navigator.clipboard.writeText(webhookUrl);
    copied = true;
    setTimeout(() => (copied = false), 2000);
  }

  $effect(() => { load(); });
</script>

<div class="space-y-5">
  <!-- Repo info -->
  <form onsubmit={handleSave} class="space-y-4">
    <div class="grid grid-cols-2 gap-3">
      <div>
        <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">
          {$t('integration.repoOwner')}
        </label>
        <input
          type="text"
          bind:value={repoOwner}
          placeholder="your-org"
          class="w-full text-sm px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
      </div>
      <div>
        <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">
          {$t('integration.repoName')}
        </label>
        <input
          type="text"
          bind:value={repoName}
          placeholder="your-repo"
          class="w-full text-sm px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
      </div>
    </div>

    <div>
      <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">
        {$t('integration.webhookSecret')}
      </label>
      <input
        type="text"
        bind:value={secret}
        placeholder={$t('integration.webhookSecretPlaceholder')}
        class="w-full text-sm px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500"
      />
    </div>

    <div class="flex justify-end">
      <button
        type="submit"
        disabled={saving || saved}
        class="px-4 py-2 text-sm font-medium rounded-lg transition-colors
               {saved ? 'bg-green-500 text-white' : 'bg-brand-500 hover:bg-brand-600 text-white disabled:opacity-50'}"
      >
        {saved ? $t('common.saved') : saving ? $t('common.saving') : $t('common.save')}
      </button>
    </div>
  </form>

  <!-- Setup instructions -->
  <div class="border-t border-slate-100 dark:border-slate-700 pt-4 space-y-3">
    <p class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
      {$t('integration.setupGuide')}
    </p>

    <ol class="space-y-2 text-xs text-slate-600 dark:text-slate-300 list-decimal list-inside">
      <li>{$t('integration.step1')}</li>
      <li>{$t('integration.step2')}</li>
      <li>
        {$t('integration.step3')}
        <div class="mt-1.5 flex items-center gap-2">
          <code class="flex-1 block bg-slate-100 dark:bg-slate-800 rounded px-2 py-1 font-mono text-[11px] text-slate-700 dark:text-slate-300 break-all">
            {webhookUrl}
          </code>
          <button
            type="button"
            onclick={copyUrl}
            class="shrink-0 px-2 py-1 text-[11px] rounded border border-slate-200 dark:border-slate-600 text-slate-500 dark:text-slate-400 hover:text-brand-600 dark:hover:text-brand-400 transition-colors"
          >
            {copied ? '✓' : $t('common.copy')}
          </button>
        </div>
      </li>
      <li>{$t('integration.step4')}</li>
      <li>{$t('integration.step5')}</li>
    </ol>

    <div class="bg-slate-50 dark:bg-slate-800 rounded-lg p-3 text-xs text-slate-500 dark:text-slate-400">
      💡 {$t('integration.keywordTip')}
      <code class="bg-white dark:bg-slate-700 px-1 rounded">fixes PROJ-42</code>,
      <code class="bg-white dark:bg-slate-700 px-1 rounded">closes PROJ-42</code>,
      <code class="bg-white dark:bg-slate-700 px-1 rounded">resolves PROJ-42</code>
    </div>
  </div>
</div>
