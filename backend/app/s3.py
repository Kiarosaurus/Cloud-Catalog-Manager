"""
Integración con AWS S3 vía boto3.
Usa las 3 credenciales temporales de AWS Academy (incluye session_token).
Sube la imagen de perfil del usuario y devuelve la URL pública del objeto.
"""
import uuid

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException

from .config import settings

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


def _get_s3_client():
    return boto3.client(
        "s3",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
        aws_session_token=settings.AWS_SESSION_TOKEN or None,
    )


def upload_image(file_bytes: bytes, content_type: str, filename: str) -> str:
    if not settings.S3_BUCKET_NAME:
        raise HTTPException(status_code=500, detail="S3_BUCKET_NAME no configurado")
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Tipo de imagen no permitido: {content_type}")

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    key = f"profiles/{uuid.uuid4().hex}.{ext}"

    base_args = dict(
        Bucket=settings.S3_BUCKET_NAME,
        Key=key,
        Body=file_bytes,
        ContentType=content_type,
    )

    try:
        client = _get_s3_client()
        try:
            # Marca el objeto como público para que la URL virtual-hosted sea
            # accesible por el navegador (GET anónimo). Requiere que el bucket
            # NO bloquee ACLs públicas.
            client.put_object(**base_args, ACL="public-read")
        except ClientError as acl_exc:
            code = acl_exc.response.get("Error", {}).get("Code", "")
            # Bucket con ACLs deshabilitadas (Object Ownership = BucketOwnerEnforced)
            # o ACL pública bloqueada -> reintenta SIN ACL para no romper el upload.
            # En ese caso la lectura pública debe habilitarse con BUCKET POLICY.
            if code in ("AccessControlListNotSupported", "InvalidArgument", "AccessDenied"):
                client.put_object(**base_args)
            else:
                raise
    except (BotoCoreError, ClientError) as exc:
        # Causa típica: token de Academy caducado -> repegar credenciales en .env
        raise HTTPException(status_code=502, detail=f"Error subiendo a S3: {exc}")

    return f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
