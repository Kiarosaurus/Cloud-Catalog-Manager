"""
Seed idempotente del usuario Admin inicial (se ejecuta al arrancar).
Si el usuario ya existe, no hace nada.
"""
from sqlalchemy.orm import Session

from .auth import hash_password
from .config import settings
from .models import AdminUser


def seed_admin(db: Session) -> None:
    existing = (
        db.query(AdminUser)
        .filter(AdminUser.username == settings.ADMIN_USERNAME)
        .first()
    )
    if existing:
        return

    admin = AdminUser(
        username=settings.ADMIN_USERNAME,
        hashed_password=hash_password(settings.ADMIN_PASSWORD),
    )
    db.add(admin)
    db.commit()
