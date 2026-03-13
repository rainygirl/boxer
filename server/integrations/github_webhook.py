import hashlib
import hmac
import json
import re

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

CLOSE_RE = re.compile(
    r'\b(?:fix(?:es|ed)?|close[sd]?|resolve[sd]?)\s+([A-Z]{1,5}-\d+)',
    re.IGNORECASE,
)
REF_RE = re.compile(r'\b([A-Z]{1,5}-\d+)\b')


def _verify_signature(secret: str, body: bytes, signature_header: str) -> bool:
    if not signature_header or not signature_header.startswith('sha256='):
        return False
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f'sha256={expected}', signature_header)


def _extract_refs(text: str):
    """Return (closing_refs, plain_refs) as sets of 'KEY-N' strings."""
    closing = {m.upper() for m in CLOSE_RE.findall(text)}
    all_refs = {m.upper() for m in REF_RE.findall(text)}
    plain = all_refs - closing
    return closing, plain


@csrf_exempt
@require_POST
def github_webhook_view(request: HttpRequest, project_id):
    from integrations.models import GitHubIntegration
    from tasks.models import Task, TaskActivity
    from integrations.dispatcher import dispatch_webhook

    try:
        integration = GitHubIntegration.objects.select_related('project').get(
            project_id=project_id
        )
    except GitHubIntegration.DoesNotExist:
        return JsonResponse({'error': 'integration not configured'}, status=404)

    if integration.webhook_secret:
        sig = request.headers.get('X-Hub-Signature-256', '')
        if not _verify_signature(integration.webhook_secret, request.body, sig):
            return JsonResponse({'error': 'invalid signature'}, status=400)

    event = request.headers.get('X-GitHub-Event', '')
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'invalid json'}, status=400)

    texts = []  # (text, url, author, is_merge)

    if event == 'push':
        for commit in payload.get('commits', []):
            texts.append((
                commit.get('message', ''),
                commit.get('url', ''),
                commit.get('author', {}).get('name', ''),
                False,
            ))
    elif event == 'pull_request':
        action = payload.get('action', '')
        pr = payload.get('pull_request', {})
        is_merge = action == 'closed' and pr.get('merged', False)
        if action in ('opened', 'synchronize') or is_merge:
            text = f"{pr.get('title', '')} {pr.get('body', '') or ''}"
            texts.append((text, pr.get('html_url', ''), pr.get('user', {}).get('login', ''), is_merge))
    else:
        return JsonResponse({'ok': True, 'skipped': True})

    project = integration.project
    activity_type = 'github_pr' if event == 'pull_request' else 'github_push'

    for text, url, author, is_merge in texts:
        closing_refs, plain_refs = _extract_refs(text)
        all_refs = closing_refs | plain_refs

        for ref in all_refs:
            try:
                key, num = ref.rsplit('-', 1)
                num = int(num)
            except ValueError:
                continue

            if key != project.key:
                continue

            try:
                task = Task.objects.get(project=project, number=num, parent_task__isnull=True)
            except Task.DoesNotExist:
                continue

            TaskActivity.objects.create(
                task=task,
                user=None,
                activity_type=activity_type,
                data={
                    'ref': ref,
                    'message': text[:200],
                    'url': url,
                    'author': author,
                },
            )

            if ref in closing_refs and is_merge:
                old_status = task.status
                if old_status not in ('done', 'confirmed', 'cancelled'):
                    task.status = 'done'
                    task.save(update_fields=['status', 'updated_at'])
                    TaskActivity.objects.create(
                        task=task,
                        user=None,
                        activity_type='status_changed',
                        data={'from': old_status, 'to': 'done', 'via': 'github'},
                    )
                    dispatch_webhook(
                        str(project.id),
                        'task.status_changed',
                        {
                            'task_id': str(task.id),
                            'task_ref': ref,
                            'task_title': task.title,
                            'status': 'done',
                            'previous_status': old_status,
                        },
                    )

    return JsonResponse({'ok': True})
