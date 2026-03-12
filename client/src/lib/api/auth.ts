import { api } from './client';
import type { User } from '$lib/types';

export const authApi = {
  me: () => api.get<User>('/auth/me').then((r) => r.data),
  updateProfile: (name: string) =>
    api.patch<User>('/auth/me', { name }).then((r) => r.data),
};
