<script lang="ts">
  import { authStore } from '$lib/stores/auth';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import Toast from '$lib/components/Toast.svelte';
  import SearchModal from '$lib/components/SearchModal.svelte';
  import QuickCreateModal from '$lib/components/QuickCreateModal.svelte';
  import { sidebarOpen } from '$lib/stores/sidebar';

  const { data, children } = $props();

  let showSearch = $state(false);
  let showQuickCreate = $state(false);

  $effect(() => {
    authStore.setUser(data.user);
  });

  function onGlobalKeydown(e: KeyboardEvent) {
    // Cmd+K / Ctrl+K → search
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      showSearch = true;
      return;
    }
    // C key → quick create (only when not in an input/textarea/contenteditable)
    if (e.key === 'c' && !e.metaKey && !e.ctrlKey && !e.altKey) {
      const target = e.target as HTMLElement;
      const tag = target.tagName.toLowerCase();
      if (tag === 'input' || tag === 'textarea' || target.isContentEditable) return;
      showQuickCreate = true;
    }
  }
</script>

<svelte:window onkeydown={onGlobalKeydown} />

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

{#if showSearch}
  <SearchModal onClose={() => (showSearch = false)} />
{/if}

{#if showQuickCreate}
  <QuickCreateModal
    projects={data.projects}
    onClose={() => (showQuickCreate = false)}
  />
{/if}
