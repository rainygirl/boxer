import { api } from './client';
import type { Task, TaskStatus, TaskPriority, TaskAttachment, TaskActivity, TaskDependencies, SubTask } from '$lib/types';

export interface TaskCreate {
  title: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  assignee_id?: number | null;
  due_date?: string | null;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  assignee_id?: number | null;
  due_date?: string | null;
}

export interface SubTaskCreate {
  title: string;
  assignee_id?: number | null;
}

export interface SubTaskUpdate {
  title?: string;
  assignee_id?: number | null;
  is_done?: boolean;
}

export const tasksApi = {
  myIssues: () =>
    api.get<Task[]>('/tasks/my').then((r) => r.data),
  list: (projectId: string) =>
    api.get<Task[]>(`/tasks/project/${projectId}`).then((r) => r.data),
  create: (projectId: string, data: TaskCreate) =>
    api.post<Task>(`/tasks/project/${projectId}`, data).then((r) => r.data),
  update: (taskId: string, data: TaskUpdate) =>
    api.patch<Task>(`/tasks/${taskId}`, data).then((r) => r.data),
  move: (taskId: string, status: TaskStatus, sort_order: number, project_id?: string) =>
    api.patch<Task>(`/tasks/${taskId}/move`, { status, sort_order, project_id }).then((r) => r.data),
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
  listActivities: (taskId: string) =>
    api.get<TaskActivity[]>(`/tasks/${taskId}/activities`).then((r) => r.data),

  listDependencies: (taskId: string) =>
    api.get<TaskDependencies>(`/tasks/${taskId}/dependencies`).then((r) => r.data),
  addDependency: (taskId: string, blockingTaskId: string) =>
    api.post<TaskDependencies>(`/tasks/${taskId}/dependencies`, { blocking_task_id: blockingTaskId }).then((r) => r.data),
  removeDependency: (taskId: string, blockingTaskId: string) =>
    api.delete(`/tasks/${taskId}/dependencies/${blockingTaskId}`),

  listSubtasks: (taskId: string) =>
    api.get<SubTask[]>(`/tasks/${taskId}/subtasks`).then((r) => r.data),
  createSubtask: (taskId: string, data: SubTaskCreate) =>
    api.post<SubTask>(`/tasks/${taskId}/subtasks`, data).then((r) => r.data),
  updateSubtask: (taskId: string, subtaskId: string, data: SubTaskUpdate) =>
    api.patch<SubTask>(`/tasks/${taskId}/subtasks/${subtaskId}`, data).then((r) => r.data),
  deleteSubtask: (taskId: string, subtaskId: string) =>
    api.delete(`/tasks/${taskId}/subtasks/${subtaskId}`),
};
