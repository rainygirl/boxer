export const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set([]),
	mimeTypes: {},
	_: {
		client: {start:"_app/immutable/entry/start.pKm6KmyO.js",app:"_app/immutable/entry/app.BISGhH_s.js",imports:["_app/immutable/entry/start.pKm6KmyO.js","_app/immutable/chunks/BOXiGsRK.js","_app/immutable/chunks/BG14EFr2.js","_app/immutable/chunks/IjrJCv2a.js","_app/immutable/chunks/BUApaBEI.js","_app/immutable/entry/app.BISGhH_s.js","_app/immutable/chunks/BG14EFr2.js","_app/immutable/chunks/CBhWZUtv.js","_app/immutable/chunks/Dp9ZGGoO.js","_app/immutable/chunks/IjrJCv2a.js","_app/immutable/chunks/aPJAeQ2k.js","_app/immutable/chunks/DnTt7h0B.js","_app/immutable/chunks/sakOKPgN.js","_app/immutable/chunks/Drck0Adj.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./nodes/0.js')),
			__memo(() => import('./nodes/1.js')),
			__memo(() => import('./nodes/2.js')),
			__memo(() => import('./nodes/3.js')),
			__memo(() => import('./nodes/4.js')),
			__memo(() => import('./nodes/5.js')),
			__memo(() => import('./nodes/6.js')),
			__memo(() => import('./nodes/7.js'))
		],
		remotes: {
			
		},
		routes: [
			{
				id: "/",
				pattern: /^\/$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 3 },
				endpoint: null
			},
			{
				id: "/app",
				pattern: /^\/app\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 4 },
				endpoint: null
			},
			{
				id: "/app/project/[projectId]",
				pattern: /^\/app\/project\/([^/]+?)\/?$/,
				params: [{"name":"projectId","optional":false,"rest":false,"chained":false}],
				page: { layouts: [0,2,], errors: [1,,], leaf: 5 },
				endpoint: null
			},
			{
				id: "/auth/callback",
				pattern: /^\/auth\/callback\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 6 },
				endpoint: null
			},
			{
				id: "/login",
				pattern: /^\/login\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 7 },
				endpoint: null
			}
		],
		prerendered_routes: new Set([]),
		matchers: async () => {
			
			return {  };
		},
		server_assets: {}
	}
}
})();
