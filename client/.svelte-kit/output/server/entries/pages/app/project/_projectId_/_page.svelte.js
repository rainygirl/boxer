import { d as attr_style, s as stringify, e as escape_html, c as attr_class, f as store_get, u as unsubscribe_stores, h as derived, b as attr, a as ensure_array_like } from "../../../../../chunks/root.js";
import { i as invalidate } from "../../../../../chunks/client.js";
import { w as writable } from "../../../../../chunks/exports.js";
import { p as page } from "../../../../../chunks/stores.js";
import "../../../../../chunks/client2.js";
import { t as tasksApi } from "../../../../../chunks/tasks.js";
const viewMode = writable("board");
const TASK_STATUSES = [
  { value: "backlog", label: "Backlog", color: "text-slate-500", bg: "bg-slate-100" },
  { value: "todo", label: "Todo", color: "text-blue-600", bg: "bg-blue-50" },
  { value: "in_progress", label: "In Progress", color: "text-amber-600", bg: "bg-amber-50" },
  { value: "done", label: "Done", color: "text-green-600", bg: "bg-green-50" },
  { value: "confirmed", label: "Confirmed", color: "text-purple-600", bg: "bg-purple-50" },
  { value: "cancelled", label: "Cancelled", color: "text-red-500", bg: "bg-red-50" }
];
const PRIORITY_CONFIG = [
  { value: "urgent", label: "Urgent", color: "text-red-600", icon: "🔴" },
  { value: "high", label: "High", color: "text-orange-500", icon: "🟠" },
  { value: "medium", label: "Medium", color: "text-yellow-500", icon: "🟡" },
  { value: "low", label: "Low", color: "text-blue-400", icon: "🔵" },
  { value: "none", label: "None", color: "text-slate-400", icon: "⚪" }
];
function ProjectHeader($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    const { projectId } = $$props;
    const project = derived(() => store_get($$store_subs ??= {}, "$page", page).data?.projects?.find((p) => p.id === projectId) ?? null);
    $$renderer2.push(`<header class="flex items-center justify-between px-6 py-3 border-b border-slate-200 bg-white shrink-0"><div class="flex items-center gap-3">`);
    if (project()) {
      $$renderer2.push("<!--[0-->");
      $$renderer2.push(`<span class="w-3 h-3 rounded-full"${attr_style(`background-color: ${stringify(project().color)}`)}></span>`);
    } else {
      $$renderer2.push("<!--[-1-->");
    }
    $$renderer2.push(`<!--]--> <h1 class="text-base font-semibold text-slate-800">${escape_html(project()?.name ?? "...")}</h1></div> <div class="flex items-center gap-2"><div class="flex items-center bg-slate-100 rounded-lg p-0.5"><button${attr_class(`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-all ${stringify(store_get($$store_subs ??= {}, "$viewMode", viewMode) === "board" ? "bg-white text-slate-800 shadow-sm" : "text-slate-500 hover:text-slate-700")}`)}><svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"></path></svg> Board</button> <button${attr_class(`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-all ${stringify(store_get($$store_subs ??= {}, "$viewMode", viewMode) === "table" ? "bg-white text-slate-800 shadow-sm" : "text-slate-500 hover:text-slate-700")}`)}><svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg> Table</button></div> <button class="flex items-center gap-1.5 px-3 py-1.5 bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium rounded-lg transition-colors"><span class="text-base leading-none">+</span> 태스크 추가</button></div></header> `);
    {
      $$renderer2.push("<!--[-1-->");
    }
    $$renderer2.push(`<!--]-->`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
function _defineProperty(obj, key, value) {
  if (key in obj) {
    Object.defineProperty(obj, key, {
      value,
      enumerable: true,
      configurable: true,
      writable: true
    });
  } else {
    obj[key] = value;
  }
  return obj;
}
var FEATURE_FLAG_NAMES = Object.freeze({
  // This flag exists as a workaround for issue 454 (basically a browser bug) - seems like these rect values take time to update when in grid layout. Setting it to true can cause strange behaviour in the REPL for non-grid zones, see issue 470
  USE_COMPUTED_STYLE_INSTEAD_OF_BOUNDING_RECT: "USE_COMPUTED_STYLE_INSTEAD_OF_BOUNDING_RECT"
});
_defineProperty({}, FEATURE_FLAG_NAMES.USE_COMPUTED_STYLE_INSTEAD_OF_BOUNDING_RECT, false);
var _ID_TO_INSTRUCTION;
var INSTRUCTION_IDs$1 = {
  DND_ZONE_ACTIVE: "dnd-zone-active",
  DND_ZONE_DRAG_DISABLED: "dnd-zone-drag-disabled"
};
_ID_TO_INSTRUCTION = {}, _defineProperty(_ID_TO_INSTRUCTION, INSTRUCTION_IDs$1.DND_ZONE_ACTIVE, "Tab to one the items and press space-bar or enter to start dragging it"), _defineProperty(_ID_TO_INSTRUCTION, INSTRUCTION_IDs$1.DND_ZONE_DRAG_DISABLED, "This is a disabled drag and drop list"), _ID_TO_INSTRUCTION;
function TaskCard($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    const { task } = $$props;
    const priority = derived(() => PRIORITY_CONFIG.find((p) => p.value === task.priority));
    $$renderer2.push(`<div role="button" tabindex="0" class="bg-white rounded-lg border border-slate-200 p-3 cursor-pointer select-none hover:shadow-sm hover:border-slate-300 transition-all"><p class="text-sm text-slate-700 font-medium leading-snug line-clamp-2 mb-2">${escape_html(task.title)}</p> <div class="flex items-center justify-between"><span class="text-xs"${attr("title", priority()?.label)}>${escape_html(priority()?.icon)}</span> `);
    if (task.assignee) {
      $$renderer2.push("<!--[0-->");
      if (task.assignee.avatar_url) {
        $$renderer2.push("<!--[0-->");
        $$renderer2.push(`<img${attr("src", task.assignee.avatar_url)} class="w-5 h-5 rounded-full"${attr("alt", task.assignee.name)}/>`);
      } else {
        $$renderer2.push("<!--[-1-->");
        $$renderer2.push(`<div class="w-5 h-5 rounded-full bg-brand-400 text-white text-[10px] flex items-center justify-center font-medium">${escape_html(task.assignee.name[0])}</div>`);
      }
      $$renderer2.push(`<!--]-->`);
    } else {
      $$renderer2.push("<!--[-1-->");
    }
    $$renderer2.push(`<!--]--></div></div> `);
    {
      $$renderer2.push("<!--[-1-->");
    }
    $$renderer2.push(`<!--]-->`);
  });
}
function KanbanColumn($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    const {
      status,
      tasks
    } = $$props;
    $$renderer2.push(`<div class="flex flex-col w-72 shrink-0"><div class="flex items-center justify-between mb-2 px-1"><div class="flex items-center gap-2"><span${attr_class(`text-xs font-semibold px-2 py-0.5 rounded-full ${stringify(status.color)} ${stringify(status.bg)}`)}>${escape_html(status.label)}</span> <span class="text-xs text-slate-400 font-medium">${escape_html(tasks.length)}</span></div> <button class="text-slate-400 hover:text-slate-600 w-6 h-6 flex items-center justify-center rounded hover:bg-slate-100 transition-colors"${attr("title", `${stringify(status.label)}에 태스크 추가`)}>+</button></div> <div class="flex-1 rounded-xl p-2 min-h-[120px] transition-colors bg-slate-100/60"><!--[-->`);
    const each_array = ensure_array_like(tasks);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let task = each_array[$$index];
      $$renderer2.push(`<div class="mb-2">`);
      TaskCard($$renderer2, { task });
      $$renderer2.push(`<!----></div>`);
    }
    $$renderer2.push(`<!--]--> `);
    if (tasks.length === 0) {
      $$renderer2.push("<!--[0-->");
      $$renderer2.push(`<div class="flex items-center justify-center h-16 text-slate-300 text-sm pointer-events-none">드래그하여 이동</div>`);
    } else {
      $$renderer2.push("<!--[-1-->");
    }
    $$renderer2.push(`<!--]--></div></div> `);
    {
      $$renderer2.push("<!--[-1-->");
    }
    $$renderer2.push(`<!--]-->`);
  });
}
function KanbanBoard($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    const { tasks } = $$props;
    const makeColumns = (taskList) => {
      const map = Object.fromEntries(TASK_STATUSES.map((s) => [s.value, []]));
      for (const t of taskList) map[t.status].push(t);
      return map;
    };
    let columns = makeColumns(tasks);
    $$renderer2.push(`<div class="flex gap-3 h-full overflow-x-auto p-4 scrollbar-thin"><!--[-->`);
    const each_array = ensure_array_like(TASK_STATUSES);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let col = each_array[$$index];
      KanbanColumn($$renderer2, {
        status: col,
        tasks: columns[col.value]
      });
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
function TaskTable($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    const { tasks, onUpdate } = $$props;
    let sortKey = "created_at";
    const sorted = derived(() => [...tasks].sort((a, b) => {
      let cmp = 0;
      cmp = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
      return -cmp;
    }));
    async function updateTask(id, data) {
      await tasksApi.update(id, data);
      onUpdate();
    }
    function sortIcon(key) {
      return sortKey === key ? "↓" : "";
    }
    $$renderer2.push(`<div class="h-full overflow-auto scrollbar-thin"><table class="w-full text-sm border-collapse"><thead class="sticky top-0 bg-white border-b border-slate-200 z-10"><tr><!--[-->`);
    const each_array = ensure_array_like([
      ["title", "태스크"],
      ["status", "상태"],
      ["priority", "우선순위"],
      ["created_at", "생성일"]
    ]);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let [key, label] = each_array[$$index];
      $$renderer2.push(`<th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 cursor-pointer select-none hover:text-slate-700">${escape_html(label)} ${escape_html(sortIcon(key))}</th>`);
    }
    $$renderer2.push(`<!--]--><th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 w-32">담당자</th><th class="w-10"></th></tr></thead><tbody class="divide-y divide-slate-100"><!--[-->`);
    const each_array_1 = ensure_array_like(sorted());
    for (let $$index_3 = 0, $$length = each_array_1.length; $$index_3 < $$length; $$index_3++) {
      let task = each_array_1[$$index_3];
      const statusCfg = TASK_STATUSES.find((s) => s.value === task.status);
      PRIORITY_CONFIG.find((p) => p.value === task.priority);
      $$renderer2.push(`<tr class="hover:bg-slate-50 group transition-colors"><td class="px-4 py-3"><button class="text-left font-medium text-slate-700 hover:text-brand-600 transition-colors line-clamp-1">${escape_html(task.title)}</button></td><td class="px-4 py-3">`);
      $$renderer2.select(
        {
          value: task.status,
          onchange: (e) => updateTask(task.id, { status: e.currentTarget.value }),
          class: `text-xs font-medium px-2 py-1 rounded-full border-0 cursor-pointer ${stringify(statusCfg.color)} ${stringify(statusCfg.bg)}`
        },
        ($$renderer3) => {
          $$renderer3.push(`<!--[-->`);
          const each_array_2 = ensure_array_like(TASK_STATUSES);
          for (let $$index_1 = 0, $$length2 = each_array_2.length; $$index_1 < $$length2; $$index_1++) {
            let s = each_array_2[$$index_1];
            $$renderer3.option({ value: s.value }, ($$renderer4) => {
              $$renderer4.push(`${escape_html(s.label)}`);
            });
          }
          $$renderer3.push(`<!--]-->`);
        }
      );
      $$renderer2.push(`</td><td class="px-4 py-3">`);
      $$renderer2.select(
        {
          value: task.priority,
          onchange: (e) => updateTask(task.id, { priority: e.currentTarget.value }),
          class: "text-xs bg-transparent border-0 cursor-pointer"
        },
        ($$renderer3) => {
          $$renderer3.push(`<!--[-->`);
          const each_array_3 = ensure_array_like(PRIORITY_CONFIG);
          for (let $$index_2 = 0, $$length2 = each_array_3.length; $$index_2 < $$length2; $$index_2++) {
            let p = each_array_3[$$index_2];
            $$renderer3.option({ value: p.value }, ($$renderer4) => {
              $$renderer4.push(`${escape_html(p.icon)} ${escape_html(p.label)}`);
            });
          }
          $$renderer3.push(`<!--]-->`);
        }
      );
      $$renderer2.push(`</td><td class="px-4 py-3 text-xs text-slate-400">${escape_html(new Date(task.created_at).toLocaleDateString("ko-KR", { month: "short", day: "numeric" }))}</td><td class="px-4 py-3">`);
      if (task.assignee) {
        $$renderer2.push("<!--[0-->");
        $$renderer2.push(`<div class="flex items-center gap-1.5">`);
        if (task.assignee.avatar_url) {
          $$renderer2.push("<!--[0-->");
          $$renderer2.push(`<img${attr("src", task.assignee.avatar_url)} class="w-5 h-5 rounded-full" alt=""/>`);
        } else {
          $$renderer2.push("<!--[-1-->");
          $$renderer2.push(`<div class="w-5 h-5 rounded-full bg-brand-400 text-white text-[10px] flex items-center justify-center">${escape_html(task.assignee.name[0])}</div>`);
        }
        $$renderer2.push(`<!--]--> <span class="text-xs text-slate-600 truncate max-w-[80px]">${escape_html(task.assignee.name)}</span></div>`);
      } else {
        $$renderer2.push("<!--[-1-->");
        $$renderer2.push(`<span class="text-xs text-slate-300">-</span>`);
      }
      $$renderer2.push(`<!--]--></td><td class="px-2 py-3"><button class="opacity-0 group-hover:opacity-100 text-slate-300 hover:text-red-400 transition-all text-xs w-6 h-6 flex items-center justify-center">✕</button></td></tr>`);
    }
    $$renderer2.push(`<!--]--></tbody></table> `);
    if (tasks.length === 0) {
      $$renderer2.push("<!--[0-->");
      $$renderer2.push(`<div class="flex flex-col items-center justify-center py-20 text-slate-400"><p class="text-sm">태스크가 없어요. 새로 만들어보세요!</p></div>`);
    } else {
      $$renderer2.push("<!--[-1-->");
    }
    $$renderer2.push(`<!--]--></div> `);
    {
      $$renderer2.push("<!--[-1-->");
    }
    $$renderer2.push(`<!--]-->`);
  });
}
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    const { data } = $$props;
    const refresh = () => invalidate(`tasks:${data.projectId}`);
    ProjectHeader($$renderer2, { projectId: data.projectId });
    $$renderer2.push(`<!----> <div class="flex-1 overflow-hidden">`);
    if (store_get($$store_subs ??= {}, "$viewMode", viewMode) === "board") {
      $$renderer2.push("<!--[0-->");
      KanbanBoard($$renderer2, {
        projectId: data.projectId,
        tasks: data.tasks
      });
    } else {
      $$renderer2.push("<!--[-1-->");
      TaskTable($$renderer2, {
        projectId: data.projectId,
        tasks: data.tasks,
        onUpdate: refresh
      });
    }
    $$renderer2.push(`<!--]--></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};
