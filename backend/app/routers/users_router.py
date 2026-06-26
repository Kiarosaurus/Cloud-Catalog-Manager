"""
Router CRUD de usuarios administrables (protegido por JWT).
La foto de perfil se sube como multipart/form-data: los campos del usuario van
como Form(...) y el archivo opcional como UploadFile -> se sube a S3 (bucket
privado) y se guarda la S3 key en profile_image_url. Al leer, se genera una
presigned GET URL temporal para que el navegador pueda mostrar la imagen.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ..auth import get_current_admin
from ..database import get_db
from ..models import User
from ..s3 import presigned_url, upload_image
from ..schemas import UserOut

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    dependencies=[Depends(get_current_admin)],  # todo el router requiere admin
)

ALLOWED_ROLES = {"admin", "user"}
ALLOWED_STATUS = {"activo", "inactivo"}


def _validate(email: Optional[str], role: Optional[str], status_: Optional[str]) -> None:
    if email is not None and "@" not in email:
        raise HTTPException(status_code=400, detail="Email inválido")
    if role is not None and role not in ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail="role debe ser 'admin' o 'user'")
    if status_ is not None and status_ not in ALLOWED_STATUS:
        raise HTTPException(status_code=400, detail="status debe ser 'activo' o 'inactivo'")


def _read_image_key(image: Optional[UploadFile]) -> Optional[str]:
    """Sube la imagen (si la hay) y devuelve la S3 key a guardar en DB."""
    if image is None or not image.filename:
        return None
    content = image.file.read()
    return upload_image(content, image.content_type, image.filename)


def _serialize(user: User) -> UserOut:
    """ORM -> UserOut, convirtiendo la S3 key guardada en una presigned URL."""
    out = UserOut.model_validate(user)
    out.profile_image_url = presigned_url(user.profile_image_url) if user.profile_image_url else None
    return out


@router.get("/", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db)):
    return [_serialize(u) for u in db.query(User).order_by(User.id).all()]


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return _serialize(user)


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    name: str = Form(...),
    email: str = Form(...),
    role: str = Form("user"),
    status_: str = Form("activo", alias="status"),
    phone: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    _validate(email, role, status_)
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese email")

    image_key = _read_image_key(image)
    user = User(
        name=name,
        email=email,
        role=role,
        status=status_,
        phone=phone,
        profile_image_url=image_key,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _serialize(user)


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    role: Optional[str] = Form(None),
    status_: Optional[str] = Form(None, alias="status"),
    phone: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    _validate(email, role, status_)

    if email is not None and email != user.email:
        if db.query(User).filter(User.email == email).first():
            raise HTTPException(status_code=400, detail="Ya existe un usuario con ese email")
        user.email = email
    if name is not None:
        user.name = name
    if role is not None:
        user.role = role
    if status_ is not None:
        user.status = status_
    if phone is not None:
        user.phone = phone

    new_key = _read_image_key(image)
    if new_key is not None:
        user.profile_image_url = new_key

    db.commit()
    db.refresh(user)
    return _serialize(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(user)
    db.commit()
