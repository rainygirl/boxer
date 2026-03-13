// @ts-nocheck
import type { PageLoad } from './$types';

export const load = async ({ parent }: Parameters<PageLoad>[0]) => {
  const parentData = await parent();
  return { projects: parentData.projects };
};
