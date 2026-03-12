

export const index = 2;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/app/_layout.svelte.js')).default;
export const universal = {
  "ssr": false,
  "load": null
};
export const universal_id = "src/routes/app/+layout.ts";
export const imports = ["_app/immutable/nodes/2.CAifXcU-.js","_app/immutable/chunks/hp4PFHFv.js","_app/immutable/chunks/BUApaBEI.js","_app/immutable/chunks/DBdK7e17.js","_app/immutable/chunks/BG14EFr2.js","_app/immutable/chunks/Dp9ZGGoO.js","_app/immutable/chunks/BkbsydWi.js","_app/immutable/chunks/DnTt7h0B.js","_app/immutable/chunks/foMo9H6A.js","_app/immutable/chunks/IjrJCv2a.js","_app/immutable/chunks/Drck0Adj.js","_app/immutable/chunks/CBhWZUtv.js","_app/immutable/chunks/aPJAeQ2k.js","_app/immutable/chunks/Db3n7Iux.js","_app/immutable/chunks/BOXiGsRK.js"];
export const stylesheets = [];
export const fonts = [];
