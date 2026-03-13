import { error } from '@sveltejs/kit';

export const load = async ({ params, parent }) => {
  const { tasks } = await parent();
  const task = (tasks as any[]).find((t) => t.id === params.taskId);
  if (!task) throw error(404, 'Task not found');
  return { task };
};
