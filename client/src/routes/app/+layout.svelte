<script lang="ts">
  import { authStore } from '$lib/stores/auth';
  import Sidebar from '$lib/components/Sidebar.svelte';

  const { data, children } = $props();

  $effect(() => {
    authStore.setUser(data.user);
  });
</script>

<div class="flex h-screen overflow-hidden">
  <Sidebar projects={data.projects} />
  <main class="flex-1 flex flex-col overflow-hidden">
    {@render children()}
  </main>
</div>
