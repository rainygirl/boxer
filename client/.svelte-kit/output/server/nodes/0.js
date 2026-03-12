

export const index = 0;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/_layout.svelte.js')).default;
export const universal = {
  "ssr": false
};
export const universal_id = "src/routes/+layout.ts";
export const imports = ["_app/immutable/nodes/0.B8XDPd-Y.js","_app/immutable/chunks/Dp9ZGGoO.js","_app/immutable/chunks/BG14EFr2.js","_app/immutable/chunks/BkbsydWi.js","_app/immutable/chunks/DnTt7h0B.js"];
export const stylesheets = ["_app/immutable/assets/0.Nw-CI0oO.css"];
export const fonts = [];
