

export const index = 5;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/app/project/_projectId_/_page.svelte.js')).default;
export const universal = {
  "ssr": false,
  "load": null
};
export const universal_id = "src/routes/app/project/[projectId]/+page.ts";
export const imports = ["_app/immutable/nodes/5.CRJ7-jdm.js","_app/immutable/chunks/DBdK7e17.js","_app/immutable/chunks/BG14EFr2.js","_app/immutable/chunks/Dp9ZGGoO.js","_app/immutable/chunks/Drck0Adj.js","_app/immutable/chunks/IjrJCv2a.js","_app/immutable/chunks/aPJAeQ2k.js","_app/immutable/chunks/DnTt7h0B.js","_app/immutable/chunks/BOXiGsRK.js","_app/immutable/chunks/BUApaBEI.js","_app/immutable/chunks/CBhWZUtv.js","_app/immutable/chunks/Db3n7Iux.js","_app/immutable/chunks/sakOKPgN.js"];
export const stylesheets = [];
export const fonts = [];
