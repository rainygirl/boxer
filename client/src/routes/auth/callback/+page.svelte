<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { authStore } from '$lib/stores/auth';
  import { t } from '$lib/i18n';

  onMount(() => {
    const token = $page.url.searchParams.get('token');
    if (token) {
      authStore.setToken(token);
      goto('/app', { replaceState: true });
    } else {
      goto('/login?error=no_token', { replaceState: true });
    }
  });
</script>

<div class="min-h-screen flex items-center justify-center">
  <p class="text-slate-500 animate-pulse">{$t('app.loggingIn')}</p>
</div>
