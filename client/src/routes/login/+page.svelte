<script lang="ts">
  import { authStore } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { t } from '$lib/i18n';
  import { api } from '$lib/api/client';

  let clientId = $state('');
  let demoMode = $state(false);
  let loaded = $state(false);
  let demoLoading = $state(false);

  onMount(async () => {
    if ($authStore.token) { goto('/app', { replaceState: true }); return; }
    try {
      const res = await api.get<{ client_id: string; demo_mode: boolean }>('/auth/google-config');
      clientId = res.data.client_id;
      demoMode = res.data.demo_mode;
    } catch {}
    loaded = true;
  });

  function loginWithGoogle() {
    if (!clientId) return;
    window.location.href = '/accounts/google/login/';
  }

  async function loginAsGuest() {
    demoLoading = true;
    try {
      const res = await api.post<{ token: string }>('/auth/demo', {});
      authStore.setToken(res.data.token);
      goto('/app', { replaceState: true });
    } catch {
      demoLoading = false;
    }
  }
</script>

<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-brand-50 to-slate-100">
  <div class="bg-white rounded-2xl shadow-xl p-10 w-full text-center" class:max-w-sm={!loaded || clientId} class:max-w-xl={loaded && !clientId}>
    <div class="text-5xl mb-4">📦</div>
    <h1 class="text-2xl font-bold text-slate-800 mb-1">Boxer</h1>
    <p class="text-slate-500 text-sm mb-8">{$t('login.subtitle')}</p>

    {#if loaded && !clientId}
      <div class="mb-6 text-left bg-amber-50 border border-amber-200 rounded-xl p-5">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-amber-500 text-lg">⚠️</span>
          <h2 class="font-semibold text-amber-800">{$t('login.setupRequired')}</h2>
        </div>
        <p class="setup-text text-sm text-amber-700 mb-4">{@html $t('login.setupDesc')}</p>
        <ol class="setup-text list-decimal list-inside space-y-2 text-sm text-slate-700 mb-4">
          <li>{@html $t('login.setupStep1')}</li>
          <li>{@html $t('login.setupStep2')}</li>
          <li>{@html $t('login.setupStep3')}</li>
        </ol>
        <pre class="bg-slate-900 text-green-400 text-xs rounded-lg p-4 text-left overflow-x-auto">GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret</pre>
      </div>
    {/if}

    {#if demoMode}
      <button
        onclick={loginAsGuest}
        disabled={demoLoading}
        class="w-full flex items-center justify-center gap-3 px-4 py-3 bg-brand-500 hover:bg-brand-600 text-white font-medium rounded-xl transition-all shadow-sm disabled:opacity-50 mb-3"
      >
        {#if demoLoading}
          <span class="animate-pulse">로딩 중...</span>
        {:else}
          <span>🚀</span>
          <span>로그인 없이 체험하기</span>
        {/if}
      </button>
      {#if clientId}
        <div class="relative flex items-center gap-3 mb-3">
          <div class="flex-1 h-px bg-slate-200"></div>
          <span class="text-xs text-slate-400">또는</span>
          <div class="flex-1 h-px bg-slate-200"></div>
        </div>
      {/if}
    {/if}

    {#if clientId}
      <button
        onclick={loginWithGoogle}
        class="w-full flex items-center justify-center gap-3 px-4 py-3 border border-slate-200 rounded-xl text-slate-700 font-medium hover:bg-slate-50 hover:border-slate-300 transition-all shadow-sm"
      >
        <svg class="w-5 h-5" viewBox="0 0 24 24">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
        </svg>
        {$t('login.continue')}
      </button>
    {/if}

    <p class="mt-6 mb-1">
      <a href="https://rainygirl.com" target="_blank" rel="noopener noreferrer" class="text-xs text-slate-400 hover:text-slate-600 transition-colors">Made by rainygirl.com</a>
    </p>
    <p class="mb-2">
      <a href="https://github.com/rainygirl/boxer" target="_blank" rel="noopener noreferrer" class="text-xs text-slate-400 hover:text-slate-600 transition-colors">github.com/rainygirl/boxer</a>
    </p>
  </div>
</div>

<style>
  :global(.setup-text code) {
    background-color: #fef3c7;
    color: #92400e;
    padding: 1px 5px;
    border-radius: 4px;
    font-size: 0.8em;
    font-family: ui-monospace, monospace;
    word-break: break-all;
  }
</style>
