import { api } from './client';
import type { User } from '$lib/types';

export const authApi = {
  me: () => api.get<User>('/auth/me').then((r) => r.data),
  updateProfile: (name: string, job_title: string = '') =>
    api.patch<User>('/auth/me', { name, job_title }).then((r) => r.data),
};
