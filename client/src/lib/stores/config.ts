import { writable } from 'svelte/store';

interface AppConfig {
  disableFileUpload: boolean;
}

export const configStore = writable<AppConfig>({
  disableFileUpload: false,
});
