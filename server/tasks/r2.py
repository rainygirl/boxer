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
