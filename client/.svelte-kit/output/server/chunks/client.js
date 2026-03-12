import "clsx";
import "@sveltejs/kit/internal";
import { w as writable } from "./exports.js";
import "./utils.js";
import "@sveltejs/kit/internal/server";
import "./root.js";
import "./state.svelte.js";
function create_updated_store() {
  const { set, subscribe } = writable(false);
  {
    return {
      subscribe,
      // eslint-disable-next-line @typescript-eslint/require-await
      check: async () => false
    };
  }
}
const stores = {
  updated: /* @__PURE__ */ create_updated_store()
};
function invalidate(resource) {
  {
    throw new Error("Cannot call invalidate(...) on the server");
  }
}
export {
  invalidate as i,
  stores as s
};
