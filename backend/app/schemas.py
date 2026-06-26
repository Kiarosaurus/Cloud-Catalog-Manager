"""
Schemas Pydantic v2: validación de entrada/salida de la API.
email se mantiene como str (validación de formato '@' en el router) para
evitar la dependencia extra email-validator.
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ---------- Usuarios administrables ----------
class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    status: str
    phone: Optional[str] = None
    profile_image_url: Optional[str] = None

    # from_attributes -> serializa directamente desde el modelo ORM
    model_config = ConfigDict(from_attributes=True)


# ---------- Autenticación ----------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
