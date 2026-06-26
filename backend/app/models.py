"""
Modelos ORM.
  User       -> usuarios administrables por el perfil Admin (CRUD del lab).
                incluye foto de perfil almacenada en S3 (profile_image_url).
  AdminUser  -> perfil Admin que se autentica (login JWT). NO se administra
                desde el CRUD; solo sirve para el acceso.
"""
from sqlalchemy import Column, Integer, String

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False, default="user")          # admin | user
    status = Column(String, nullable=False, default="activo")      # activo | inactivo
    phone = Column(String, nullable=True)
    profile_image_url = Column(String, nullable=True)              # S3 key de la foto (profiles/uuid.ext); se firma al leer


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
