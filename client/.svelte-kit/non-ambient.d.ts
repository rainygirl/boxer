
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
		RouteId(): "/" | "/app" | "/app/my-issues" | "/app/project" | "/app/project/[projectId]" | "/app/project/[projectId]/issue" | "/app/project/[projectId]/issue/[taskId]" | "/auth" | "/auth/callback" | "/login";
		RouteParams(): {
			"/app/project/[projectId]": { projectId: string };
			"/app/project/[projectId]/issue": { projectId: string };
			"/app/project/[projectId]/issue/[taskId]": { projectId: string; taskId: string }
		};
		LayoutParams(): {
			"/": { projectId?: string; taskId?: string };
			"/app": { projectId?: string; taskId?: string };
			"/app/my-issues": Record<string, never>;
			"/app/project": { projectId?: string; taskId?: string };
			"/app/project/[projectId]": { projectId: string; taskId?: string };
			"/app/project/[projectId]/issue": { projectId: string; taskId?: string };
			"/app/project/[projectId]/issue/[taskId]": { projectId: string; taskId: string };
			"/auth": Record<string, never>;
			"/auth/callback": Record<string, never>;
			"/login": Record<string, never>
		};
		Pathname(): "/" | "/app" | "/app/my-issues" | `/app/project/${string}` & {} | `/app/project/${string}/issue/${string}` & {} | "/auth/callback" | "/login";
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): string & {};
	}
}