<script lang="ts">
  import { authStore } from '$lib/stores/auth';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import Toast from '$lib/components/Toast.svelte';
  import QuickCreateModal from '$lib/components/QuickCreateModal.svelte';
  import { sidebarOpen } from '$lib/stores/sidebar';

  const { data, children } = $props();

  let showQuickCreate = $state(false);

  $effect(() => {
    authStore.setUser(data.user);
  });
</script>

<div class="flex h-screen overflow-hidden">
  <Sidebar projects={data.projects} />
  <!-- Mobile backdrop -->
  {#if $sidebarOpen}
    <div
      class="fixed inset-0 z-30 bg-black/50 md:hidden"
      onclick={() => sidebarOpen.set(false)}
    ></div>
  {/if}
  <main class="flex-1 flex flex-col overflow-hidden min-w-0">
    {@render children()}
  </main>
</div>

<Toast />

{#if showQuickCreate}
  <QuickCreateModal
    projects={data.projects}
    onClose={() => (showQuickCreate = false)}
  />
{/if}
