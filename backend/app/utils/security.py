"""Utilidades de seguridad: hashing de contraseñas y JWT (spec §13.1).

- Contraseñas: bcrypt (passlib).
- Tokens: JWT firmados con SECRET_KEY (python-jose). Access token corto (30 min)
  + refresh token largo. El `sub` del token es el id del usuario.
"""
from datetime import datetime, timedelta, timezone

from cryptography.fernet import Fernet
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- Encriptación de credenciales de servicio (Fernet, spec §13.2) ---
class CredentialEncryptor:
    """Encripta/desencripta credenciales (Gmail App Password, Dropbox Token).

    Se guardan SIEMPRE encriptadas en la tabla `users`; el frontend nunca recibe
    la credencial en claro, solo el estado (conectado / no conectado).
    """

    def __init__(self, encryption_key: str):
        self.cipher = Fernet(encryption_key.encode())

    def encrypt(self, plaintext: str) -> str:
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        return self.cipher.decrypt(ciphertext.encode()).decode()


# Instancia única, lista para usar en los endpoints de credenciales.
encryptor = CredentialEncryptor(settings.ENCRYPTION_KEY)


# --- Contraseñas ---
def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# --- JWT ---
def _create_token(sub: str, expires_delta: timedelta, token_type: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(sub),
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(sub: str) -> str:
    return _create_token(
        sub,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "access",
    )


def create_refresh_token(sub: str) -> str:
    return _create_token(
        sub,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "refresh",
    )


def decode_token(token: str) -> dict | None:
    """Devuelve el payload si el token es válido y no ha expirado; si no, None."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
