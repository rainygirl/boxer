import { writable } from 'svelte/store';

interface AppConfig {
  disableFileUpload: boolean;
  demoMode: boolean;
  demoProjectId: string;
}

export const configStore = writable<AppConfig>({
  disableFileUpload: false,
  demoMode: false,
  demoProjectId: '',
});
