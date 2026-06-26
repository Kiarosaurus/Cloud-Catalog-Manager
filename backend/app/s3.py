"""
Integración con AWS S3 vía boto3.
Usa las 3 credenciales temporales de AWS Academy (incluye session_token).

Estrategia de acceso: el bucket permanece PRIVADO. La imagen se sube sin ACL
(compatible con buckets que tienen Block Public Access activo / Object Ownership
= BucketOwnerEnforced) y se guarda solo la S3 key en la base de datos. Para
mostrarla, se genera una presigned GET URL temporal al momento de leer.
"""
import uuid
from urllib.parse import urlparse

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException

from .config import settings

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}

# Vigencia de la presigned URL (segundos). Se regenera en cada lectura, así que
# basta con que cubra la vida útil de una vista. Limitada además por la caducidad
# del session token temporal de Academy.
PRESIGNED_EXPIRES = 3600


def _get_s3_client():
    return boto3.client(
        "s3",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
        aws_session_token=settings.AWS_SESSION_TOKEN or None,
    )


def upload_image(file_bytes: bytes, content_type: str, filename: str) -> str:
    """Sube la imagen a S3 (bucket privado) y devuelve la S3 key."""
    if not settings.S3_BUCKET_NAME:
        raise HTTPException(status_code=500, detail="S3_BUCKET_NAME no configurado")
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Tipo de imagen no permitido: {content_type}")

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    key = f"profiles/{uuid.uuid4().hex}.{ext}"

    try:
        client = _get_s3_client()
        # Sin ACL: el objeto queda privado. La lectura se hace con presigned URL.
        client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=key,
            Body=file_bytes,
            ContentType=content_type,
        )
    except (BotoCoreError, ClientError) as exc:
        # Causa típica: token de Academy caducado -> repegar credenciales en .env
        raise HTTPException(status_code=502, detail=f"Error subiendo a S3: {exc}")

    return key


def _object_key(stored: str) -> str:
    """Normaliza el valor guardado en DB a una S3 key.

    Acepta tanto una key directa (`profiles/uuid.ext`) como una URL completa
    legada (`https://bucket.s3.region.amazonaws.com/profiles/uuid.ext`).
    """
    if stored.startswith("http://") or stored.startswith("https://"):
        return urlparse(stored).path.lstrip("/")
    return stored


def presigned_url(stored: str) -> str | None:
    """Genera una presigned GET URL temporal para la key/URL guardada."""
    if not stored or not settings.S3_BUCKET_NAME:
        return None
    try:
        client = _get_s3_client()
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET_NAME, "Key": _object_key(stored)},
            ExpiresIn=PRESIGNED_EXPIRES,
        )
    except (BotoCoreError, ClientError):
        # No romper el listado si falla la firma (p. ej. token caducado).
        return None
