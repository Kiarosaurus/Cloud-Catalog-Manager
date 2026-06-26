"""
Configuración central (Phase 2).
Lee variables del entorno / .env con pydantic-settings.
Las credenciales AWS Academy son temporales: si faltan, los campos
quedan vacíos y el upload a S3 fallará de forma controlada.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ---- Base de datos ----
    DATABASE_URL: str

    # ---- Seguridad ----
    JWT_SECRET: str

    # ---- AWS S3 (credenciales temporales Academy) ----
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_SESSION_TOKEN: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = ""

    # ---- Seed admin inicial ----
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"

    # extra='ignore' -> ignora vars del .env que no estén declaradas
    # (POSTGRES_*, VITE_API_URL son para compose/frontend, no para el backend)
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
