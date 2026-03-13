import hashlib
import hmac
import json
import threading

import requests


def dispatch_webhook(project_id, event_type: str, payload: dict):
    """Fire outgoing webhooks for a project event. Non-blocking (runs in daemon threads)."""
    from integrations.models import ProjectWebhook
    webhooks = list(
        ProjectWebhook.objects.filter(project_id=project_id, active=True)
    )
    for wh in webhooks:
        if wh.events and event_type not in wh.events:
            continue
        body = json.dumps({'event': event_type, **payload}, default=str).encode()
        headers = {
            'Content-Type': 'application/json',
            'X-Boxer-Event': event_type,
        }
        if wh.secret:
            sig = hmac.new(wh.secret.encode(), body, hashlib.sha256).hexdigest()
            headers['X-Boxer-Signature-256'] = f'sha256={sig}'
        t = threading.Thread(target=_post, args=(wh.url, body, headers), daemon=True)
        t.start()


def _post(url: str, body: bytes, headers: dict):
    try:
        requests.post(url, data=body, headers=headers, timeout=10)
    except Exception:
        pass
