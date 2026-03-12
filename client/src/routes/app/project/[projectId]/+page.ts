import { tasksApi } from '$lib/api/tasks';

export const load = async ({ params, depends }) => {
  depends(`tasks:${params.projectId}`);
  const tasks = await tasksApi.list(params.projectId);
  return { tasks, projectId: params.projectId };
};
