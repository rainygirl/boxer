import type { PageLoad } from './$types';
import { tasksApi } from '$lib/api/tasks';
import type { Task } from '$lib/types';

export const load: PageLoad = async ({ params, parent }) => {
  const parentData = await parent();
  const tasks: Task[] = await tasksApi.byUser(params.userId);
  // Find target user from project members
  const allMembers = (parentData.projects as any[]).flatMap((p: any) => p.members ?? []);
  const targetUser = allMembers.find((m: any) => String(m.user.id) === params.userId)?.user ?? null;
  return { tasks, targetUser, projects: parentData.projects };
};
