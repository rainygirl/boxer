import { api } from './client';

export interface GitHubIntegration {
  id: string;
  repo_owner: string;
  repo_name: string;
  webhook_secret: string;
  is_configured: boolean;
}

export interface ProjectWebhook {
  id: string;
  url: string;
  secret: string;
  events: string[];
  active: boolean;
}

export const WEBHOOK_EVENTS = [
  'task.created',
  'task.updated',
  'task.status_changed',
  'task.comment',
] as const;

export const integrationsApi = {
  getGitHub: (projectId: string) =>
    api.get<GitHubIntegration>(`/integrations/projects/${projectId}/github`).then((r) => r.data),
  updateGitHub: (projectId: string, data: Partial<GitHubIntegration>) =>
    api.patch<GitHubIntegration>(`/integrations/projects/${projectId}/github`, data).then((r) => r.data),

  listWebhooks: (projectId: string) =>
    api.get<ProjectWebhook[]>(`/integrations/projects/${projectId}/webhooks`).then((r) => r.data),
  createWebhook: (projectId: string, data: Omit<ProjectWebhook, 'id'>) =>
    api.post<ProjectWebhook>(`/integrations/projects/${projectId}/webhooks`, data).then((r) => r.data),
  updateWebhook: (projectId: string, webhookId: string, data: Partial<ProjectWebhook>) =>
    api.patch<ProjectWebhook>(`/integrations/projects/${projectId}/webhooks/${webhookId}`, data).then((r) => r.data),
  deleteWebhook: (projectId: string, webhookId: string) =>
    api.delete(`/integrations/projects/${projectId}/webhooks/${webhookId}`),
};
