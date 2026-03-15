import { api } from './client';
import type { User } from '$lib/types';

export const authApi = {
  me: () => api.get<User>('/auth/me').then((r) => r.data),
  updateProfile: (name: string, job_title: string = '') =>
    api.patch<User>('/auth/me', { name, job_title }).then((r) => r.data),
  getConfig: () =>
    api.get<{ client_id: string; disable_file_upload: boolean; demo_mode: boolean; demo_project_id: string }>('/auth/google-config').then((r) => r.data),
};
