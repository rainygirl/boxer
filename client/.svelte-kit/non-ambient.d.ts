
// this file is generated — do not edit it


declare module "svelte/elements" {
	export interface HTMLAttributes<T> {
		'data-sveltekit-keepfocus'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-noscroll'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-preload-code'?:
			| true
			| ''
			| 'eager'
			| 'viewport'
			| 'hover'
			| 'tap'
			| 'off'
			| undefined
			| null;
		'data-sveltekit-preload-data'?: true | '' | 'hover' | 'tap' | 'off' | undefined | null;
		'data-sveltekit-reload'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-replacestate'?: true | '' | 'off' | undefined | null;
	}
}

export {};


declare module "$app/types" {
	export interface AppTypes {
		RouteId(): "/" | "/app" | "/app/project" | "/app/project/[projectId]" | "/auth" | "/auth/callback" | "/login";
		RouteParams(): {
			"/app/project/[projectId]": { projectId: string }
		};
		LayoutParams(): {
			"/": { projectId?: string };
			"/app": { projectId?: string };
			"/app/project": { projectId?: string };
			"/app/project/[projectId]": { projectId: string };
			"/auth": Record<string, never>;
			"/auth/callback": Record<string, never>;
			"/login": Record<string, never>
		};
		Pathname(): "/" | "/app" | `/app/project/${string}` & {} | "/auth/callback" | "/login";
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): string & {};
	}
}