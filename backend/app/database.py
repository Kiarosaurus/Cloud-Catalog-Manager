"""
Capa de acceso a datos: engine + sesión SQLAlchemy 2.0.
get_db() es la dependencia FastAPI que abre/cierra sesión por request.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from .config import settings

# pool_pre_ping evita errores de conexión muerta (útil con RDS).
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
