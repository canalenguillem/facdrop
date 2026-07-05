"""Dependencias de autenticación (spec §12.3, §13.1).

Nota de diseño: la spec §12.3 propone un middleware HTTP que valida el JWT. Aquí
usamos dependencias de FastAPI (`get_current_user`, `require_admin`) en su lugar:
es más idiomático y permite exigir rol admin ruta a ruta y obtener el usuario
inyectado. El efecto es el mismo (todo `/api/` protegido salvo `/api/auth/*`).
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.utils.security import decode_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No token")

    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found or inactive")
    return user


def require_admin(current: User = Depends(get_current_user)) -> User:
    if not current.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin only")
    return current
