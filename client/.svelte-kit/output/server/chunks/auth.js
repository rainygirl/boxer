import { w as writable } from "./exports.js";
function createAuthStore() {
  const { subscribe, set, update } = writable({
    token: typeof localStorage !== "undefined" ? localStorage.getItem("boxer_token") : null,
    user: null
  });
  return {
    subscribe,
    setToken(token) {
      localStorage.setItem("boxer_token", token);
      update((s) => ({ ...s, token }));
    },
    setUser(user) {
      update((s) => ({ ...s, user }));
    },
    logout() {
      localStorage.removeItem("boxer_token");
      set({ token: null, user: null });
    }
  };
}
const authStore = createAuthStore();
export {
  authStore as a
};
