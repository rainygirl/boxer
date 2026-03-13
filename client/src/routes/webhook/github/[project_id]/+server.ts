import type { RequestHandler } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

const BACKEND_URL = env.BACKEND_URL ?? 'http://127.0.0.1:4000';

export const POST: RequestHandler = async ({ params, request }) => {
  const forwardHeaders = new Headers();
  for (const key of ['content-type', 'x-github-event', 'x-hub-signature-256', 'x-github-delivery']) {
    const val = request.headers.get(key);
    if (val) forwardHeaders.set(key, val);
  }

  const body = await request.arrayBuffer();

  const res = await fetch(
    `${BACKEND_URL}/webhook/github/${params.project_id}/`,
    { method: 'POST', headers: forwardHeaders, body },
  );

  const text = await res.text();
  return new Response(text, {
    status: res.status,
    headers: { 'content-type': 'application/json' },
  });
};
