<script lang="ts">
  import '../app.css';
  import { themeStore } from '$lib/stores/theme';
  const { children } = $props();

  $effect(() => {
    themeStore.init();
  });
</script>

{@render children()}
