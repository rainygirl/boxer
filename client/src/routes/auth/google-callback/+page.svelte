<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { authStore } from '$lib/stores/auth';
  import { api } from '$lib/api/client';
  import { t } from '$lib/i18n';

  let error = $state('');

  onMount(async () => {
    const code = $page.url.searchParams.get('code');
    if (!code) {
      goto('/login?error=no_code', { replaceState: true });
      return;
    }

    const redirectUri = `${window.location.origin}/auth/google-callback`;
    try {
      const res = await api.post<{ token: string }>('/auth/google', {
        code,
        redirect_uri: redirectUri,
      });
      authStore.setToken(res.data.token);
      goto('/app', { replaceState: true });
    } catch (e: any) {
      error = e?.response?.data?.detail ?? 'Login failed';
    }
  });
</script>

<div class="min-h-screen flex items-center justify-center">
  {#if error}
    <div class="text-center">
      <p class="text-red-500 text-sm mb-4">{error}</p>
      <a href="/login" class="text-brand-600 text-sm hover:underline">다시 로그인</a>
    </div>
  {:else}
    <p class="text-slate-500 animate-pulse">{$t('app.loggingIn')}</p>
  {/if}
</div>
