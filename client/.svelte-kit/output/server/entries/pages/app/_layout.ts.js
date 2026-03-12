import { redirect } from "@sveltejs/kit";
import { a as api } from "../../../chunks/client2.js";
const projectsApi = {
  list: () => api.get("/projects/").then((r) => r.data),
  get: (id) => api.get(`/projects/${id}`).then((r) => r.data),
  create: (data) => api.post("/projects/", data).then((r) => r.data),
  update: (id, data) => api.patch(`/projects/${id}`, data).then((r) => r.data),
  delete: (id) => api.delete(`/projects/${id}`)
};
const authApi = {
  me: () => api.get("/auth/me").then((r) => r.data)
};
const load = async () => {
  const token = localStorage.getItem("boxer_token");
  if (!token) redirect(302, "/login");
  const [user, projects] = await Promise.all([authApi.me(), projectsApi.list()]);
  return { user, projects };
};
export {
  load
};
