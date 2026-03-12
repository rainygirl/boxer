import "clsx";
import { a as authStore } from "../../../chunks/auth.js";
import { a as ensure_array_like, b as attr, s as stringify, c as attr_class, d as attr_style, e as escape_html, f as store_get, u as unsubscribe_stores, h as derived } from "../../../chunks/root.js";
import { p as page } from "../../../chunks/stores.js";
import "@sveltejs/kit/internal";
import "../../../chunks/exports.js";
import "../../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../../chunks/state.svelte.js";
import "../../../chunks/client2.js";
function Sidebar($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    const { projects } = $$props;
    let deleting = null;
    const currentProjectId = derived(() => store_get($$store_subs ??= {}, "$page", page).params.projectId);
    $$renderer2.push(`<aside class="w-60 bg-white border-r border-slate-200 flex flex-col h-full shrink-0"><div class="px-4 py-4 border-b border-slate-100"><div class="flex items-center gap-2"><span class="text-xl">📦</span> <span class="font-bold text-slate-800 text-lg">Boxer</span></div></div> <div class="flex-1 overflow-y-auto py-3 scrollbar-thin"><div class="flex items-center justify-between px-4 mb-1"><span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">프로젝트</span> <button class="text-slate-400 hover:text-brand-600 transition-colors text-lg leading-none" title="새 프로젝트">+</button></div> <nav class="space-y-0.5 px-2"><!--[-->`);
    const each_array = ensure_array_like(projects);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let p = each_array[$$index];
      $$renderer2.push(`<a${attr("href", `/app/project/${stringify(p.id)}`)}${attr_class(`flex items-center gap-2.5 px-2 py-2 rounded-lg text-sm transition-colors group ${stringify(currentProjectId() === p.id ? "bg-brand-50 text-brand-700 font-medium" : "text-slate-600 hover:bg-slate-50")}`)}><span class="w-2.5 h-2.5 rounded-full shrink-0"${attr_style(`background-color: ${stringify(p.color)}`)}></span> <span class="flex-1 truncate">${escape_html(p.name)}</span> `);
      if (currentProjectId() === p.id) {
        $$renderer2.push("<!--[0-->");
        $$renderer2.push(`<button${attr("disabled", deleting === p.id, true)} class="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-red-500 transition-all text-xs px-1">✕</button>`);
      } else {
        $$renderer2.push("<!--[-1-->");
      }
      $$renderer2.push(`<!--]--></a>`);
    }
    $$renderer2.push(`<!--]--></nav> `);
    if (projects.length === 0) {
      $$renderer2.push("<!--[0-->");
      $$renderer2.push(`<p class="px-4 text-xs text-slate-400 mt-2">아직 프로젝트가 없어요.</p>`);
    } else {
      $$renderer2.push("<!--[-1-->");
    }
    $$renderer2.push(`<!--]--></div> <div class="border-t border-slate-100 p-3">`);
    if (store_get($$store_subs ??= {}, "$authStore", authStore).user) {
      $$renderer2.push("<!--[0-->");
      const user = store_get($$store_subs ??= {}, "$authStore", authStore).user;
      $$renderer2.push(`<div class="flex items-center gap-2 px-2 py-2 rounded-lg hover:bg-slate-50 group cursor-default">`);
      if (user.avatar_url) {
        $$renderer2.push("<!--[0-->");
        $$renderer2.push(`<img${attr("src", user.avatar_url)} class="w-7 h-7 rounded-full"${attr("alt", user.name)}/>`);
      } else {
        $$renderer2.push("<!--[-1-->");
        $$renderer2.push(`<div class="w-7 h-7 rounded-full bg-brand-500 text-white text-xs flex items-center justify-center font-medium">${escape_html(user.name[0])}</div>`);
      }
      $$renderer2.push(`<!--]--> <div class="flex-1 min-w-0"><p class="text-sm font-medium text-slate-700 truncate">${escape_html(user.name)}</p> <p class="text-xs text-slate-400 truncate">${escape_html(user.email)}</p></div> <button class="opacity-0 group-hover:opacity-100 text-xs text-slate-400 hover:text-slate-600 transition-all" title="로그아웃">↩</button></div>`);
    } else {
      $$renderer2.push("<!--[-1-->");
    }
    $$renderer2.push(`<!--]--></div></aside> `);
    {
      $$renderer2.push("<!--[-1-->");
    }
    $$renderer2.push(`<!--]-->`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
function _layout($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    const { data, children } = $$props;
    $$renderer2.push(`<div class="flex h-screen overflow-hidden">`);
    Sidebar($$renderer2, { projects: data.projects });
    $$renderer2.push(`<!----> <main class="flex-1 flex flex-col overflow-hidden">`);
    children($$renderer2);
    $$renderer2.push(`<!----></main></div>`);
  });
}
export {
  _layout as default
};
