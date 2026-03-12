import { tasksApi } from '$lib/api/tasks';

export const load = async ({ parent }) => {
  const { projects } = await parent();
  const tasks = await tasksApi.myIssues();
  return { tasks, projects };
};
