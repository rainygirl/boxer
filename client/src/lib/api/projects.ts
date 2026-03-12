import { api } from './client';
import type { Project, ProjectMember } from '$lib/types';

export interface ProjectCreate {
  name: string;
  description?: string;
  color?: string;
  key?: string;
}

export const projectsApi = {
  list: () => api.get<Project[]>('/projects/').then((r) => r.data),
  get: (id: string) => api.get<Project>(`/projects/${id}`).then((r) => r.data),
  create: (data: ProjectCreate) => api.post<Project>('/projects/', data).then((r) => r.data),
  update: (id: string, data: Partial<ProjectCreate>) =>
    api.patch<Project>(`/projects/${id}`, data).then((r) => r.data),
  delete: (id: string) => api.delete(`/projects/${id}`),

  listMembers: (id: string) =>
    api.get<ProjectMember[]>(`/projects/${id}/members`).then((r) => r.data),
  inviteMember: (id: string, email: string) =>
    api.post<ProjectMember>(`/projects/${id}/members`, { email }).then((r) => r.data),
  updateMemberRole: (id: string, userId: number, role: string) =>
    api.patch<ProjectMember>(`/projects/${id}/members/${userId}`, { role }).then((r) => r.data),
  removeMember: (id: string, userId: number) =>
    api.delete(`/projects/${id}/members/${userId}`),

  updateColumns: (id: string, disabledStatuses: string[]) =>
    api.patch<Project>(`/projects/${id}/columns`, { disabled_statuses: disabledStatuses }).then((r) => r.data),
};
