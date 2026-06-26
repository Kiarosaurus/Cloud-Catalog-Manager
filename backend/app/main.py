"""
Punto de entrada FastAPI (Phase 2).
- Crea las tablas al arrancar (create_all).
- Siembra el usuario Admin inicial (seed idempotente).
- Monta routers de auth y usuarios.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, SessionLocal, engine
from .routers import auth_router, users_router
from .seed import seed_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: crear tablas + seed admin.
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_admin(db)
    finally:
        db.close()
    yield
    # Shutdown: nada que limpiar por ahora.


app = FastAPI(
    title="Gestión de Usuarios - Admin API",
    description="Backend FastAPI: JWT + CRUD usuarios + foto de perfil en S3",
    version="0.3.0",
    lifespan=lifespan,
)

# CORS abierto en desarrollo. En producción restringir allow_origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(users_router.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy"}
