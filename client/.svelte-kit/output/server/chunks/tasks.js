import { a as api } from "./client2.js";
const tasksApi = {
  list: (projectId) => api.get(`/tasks/project/${projectId}`).then((r) => r.data),
  create: (projectId, data) => api.post(`/tasks/project/${projectId}`, data).then((r) => r.data),
  update: (taskId, data) => api.patch(`/tasks/${taskId}`, data).then((r) => r.data),
  move: (taskId, status, sort_order) => api.patch(`/tasks/${taskId}/move`, { status, sort_order }).then((r) => r.data),
  delete: (taskId) => api.delete(`/tasks/${taskId}`)
};
export {
  tasksApi as t
};
