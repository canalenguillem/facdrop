"""Configuración de la app.

Carga las variables de entorno que docker-compose inyecta en el contenedor del
backend. En Fase 2 solo necesitamos las de BD / JWT / encriptación; las de
invitaciones, SMTP y admin semilla se añadirán en la Fase 3 (junto con su
inyección en docker-compose).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Bases de datos
    DATABASE_URL: str
    MONGODB_URL: str
    REDIS_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Encriptación de credenciales (Fernet)
    ENCRYPTION_KEY: str

    # Refresh token (días de validez)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Admin semilla (se crea en el primer arranque si no existe)
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    # URL pública (para construir los enlaces de invitación)
    APP_PUBLIC_URL: str = "http://localhost:15173"

    # Caducidad de las invitaciones (días)
    INVITATION_EXPIRE_DAYS: int = 7

    # SMTP (envío de emails de invitación). Opcional: si no está configurado,
    # el enlace de invitación se registra en el log en vez de enviarse.
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM: str = "Fracdrop <no-reply@fracdrop.app>"

    # Dropbox OAuth (app compartida). Si están configuradas, se ofrece el botón
    # "Conectar con Dropbox" (acceso permanente vía refresh token).
    DROPBOX_APP_KEY: str | None = None
    DROPBOX_APP_SECRET: str | None = None

    # extra="ignore": no fallar si el entorno trae variables que aún no usamos.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
