import { api } from './client';
import type { Notification } from '$lib/types';

export const notificationsApi = {
  list: () =>
    api.get<Notification[]>('/notifications/').then((r) => r.data),
  markRead: (id: string) =>
    api.patch<Notification>(`/notifications/${id}/read`).then((r) => r.data),
  markAllRead: () =>
    api.post('/notifications/read-all').then((r) => r.data),
};
