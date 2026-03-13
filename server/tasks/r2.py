import hashlib
import mimetypes
import os
import uuid

import boto3
from botocore.config import Config
from django.conf import settings


def get_r2_client():
    return boto3.client(
        's3',
        endpoint_url=f'https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        config=Config(signature_version='s3v4'),
        region_name='auto',
    )


def upload_file(file_obj, filename: str) -> dict:
    """Upload a file to R2. Returns key, content_type, size."""
    client = get_r2_client()
    ext = os.path.splitext(filename)[1]
    key = f'attachments/{uuid.uuid4()}{ext}'
    content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    content = file_obj.read()
    client.put_object(
        Bucket=settings.R2_BUCKET_NAME,
        Key=key,
        Body=content,
        ContentType=content_type,
    )
    return {'key': key, 'content_type': content_type, 'size': len(content)}


def get_presigned_url(key: str, expiry: int = 3600) -> str:
    """Generate a presigned GET URL (valid for `expiry` seconds)."""
    if settings.R2_PUBLIC_URL:
        return f'{settings.R2_PUBLIC_URL.rstrip("/")}/{key}'
    client = get_r2_client()
    return client.generate_presigned_url(
        'get_object',
        Params={'Bucket': settings.R2_BUCKET_NAME, 'Key': key},
        ExpiresIn=expiry,
    )


def delete_file(key: str):
    client = get_r2_client()
    client.delete_object(Bucket=settings.R2_BUCKET_NAME, Key=key)


def upload_avatar(user_pk, image_url: str) -> str | None:
    """Download image_url and store it in R2 under avatars/{hash}.jpg.
    Returns the public URL if R2_PUBLIC_URL is configured, otherwise None."""
    if not settings.R2_CONFIGURED or not settings.R2_PUBLIC_URL:
        return None

    import urllib.request
    try:
        req = urllib.request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read()
            content_type = resp.headers.get('Content-Type', 'image/jpeg').split(';')[0].strip()
    except Exception:
        return None

    ext = mimetypes.guess_extension(content_type) or '.jpg'
    if ext in ('.jpe', '.jpeg'):
        ext = '.jpg'

    hashed = hashlib.sha256(f'{user_pk}{settings.SECRET_KEY}'.encode()).hexdigest()[:32]
    key = f'avatars/{hashed}{ext}'
    try:
        get_r2_client().put_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=key,
            Body=content,
            ContentType=content_type,
        )
    except Exception:
        return None

    return f'{settings.R2_PUBLIC_URL.rstrip("/")}/{key}'
