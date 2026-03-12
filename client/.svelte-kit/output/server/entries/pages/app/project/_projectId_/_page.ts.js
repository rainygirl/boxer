import { t as tasksApi } from "../../../../../chunks/tasks.js";
const load = async ({ params, depends }) => {
  depends(`tasks:${params.projectId}`);
  const tasks = await tasksApi.list(params.projectId);
  return { tasks, projectId: params.projectId };
};
export {
  load
};
