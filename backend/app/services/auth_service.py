"""Servicio de autenticación: login y admin semilla (spec §9.1, §13.1)."""
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User
from app.utils.security import hash_password, verify_password


def authenticate(db: Session, email: str, password: str) -> User | None:
    """Devuelve el usuario si email+contraseña son correctos y está activo."""
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def seed_admin(db: Session) -> None:
    """Crea el admin semilla en el primer arranque si no existe (spec §9.1)."""
    exists = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
    if exists:
        return
    db.add(
        User(
            email=settings.ADMIN_EMAIL,
            username="admin",
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            is_admin=True,
            role="admin",
            is_active=True,
        )
    )
    db.commit()
