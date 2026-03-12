import { api } from './client';
import type { Task, TaskStatus, TaskPriority, TaskAttachment } from '$lib/types';

export interface TaskCreate {
  title: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  assignee_id?: number | null;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  assignee_id?: number | null;
}

export const tasksApi = {
  list: (projectId: string) =>
    api.get<Task[]>(`/tasks/project/${projectId}`).then((r) => r.data),
  create: (projectId: string, data: TaskCreate) =>
    api.post<Task>(`/tasks/project/${projectId}`, data).then((r) => r.data),
  update: (taskId: string, data: TaskUpdate) =>
    api.patch<Task>(`/tasks/${taskId}`, data).then((r) => r.data),
  move: (taskId: string, status: TaskStatus, sort_order: number) =>
    api.patch<Task>(`/tasks/${taskId}/move`, { status, sort_order }).then((r) => r.data),
  delete: (taskId: string) => api.delete(`/tasks/${taskId}`),
  listAttachments: (taskId: string) =>
    api.get<TaskAttachment[]>(`/tasks/${taskId}/attachments`).then((r) => r.data),
  uploadAttachment: (taskId: string, file: File) => {
    const form = new FormData();
    form.append('file', file);
    return api.post<TaskAttachment>(`/tasks/${taskId}/attachments`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data);
  },
  deleteAttachment: (taskId: string, attachmentId: string) =>
    api.delete(`/tasks/${taskId}/attachments/${attachmentId}`),
};
