import { redirect } from '@sveltejs/kit';
import { authApi } from '$lib/api/auth';
import { projectsApi } from '$lib/api/projects';

export const load = async ({ depends }) => {
  const token = localStorage.getItem('boxer_token');
  if (!token) redirect(302, '/login');

  depends('app:projects');
  const [user, projects, config] = await Promise.all([authApi.me(), projectsApi.list(), authApi.getConfig()]);
  return {
    user,
    projects,
    disableFileUpload: config.disable_file_upload,
    demoMode: config.demo_mode,
    demoProjectId: config.demo_project_id,
  };
};
