"""Servicio de invitaciones (spec §9).

Reglas: token aleatorio de un solo uso, con caducidad. El email queda fijado por
la invitación. Una invitación 'accepted' no se reutiliza.
"""
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.config import settings
from app.models.invitation import Invitation
from app.models.user import User


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_invitation(db: Session, email: str, role: str, invited_by: int) -> Invitation:
    """Crea una invitación 'pending' con token único y caducidad."""
    inv = Invitation(
        email=email,
        token=secrets.token_urlsafe(32),
        role=role,
        invited_by=invited_by,
        status="pending",
        expires_at=_now() + timedelta(days=settings.INVITATION_EXPIRE_DAYS),
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


def get_valid_invitation(db: Session, token: str) -> Invitation | None:
    """Devuelve la invitación si el token es válido, 'pending' y no caducado.

    Si está 'pending' pero caducada, la marca como 'expired' y devuelve None.
    """
    inv = db.query(Invitation).filter(Invitation.token == token).first()
    if not inv or inv.status != "pending":
        return None
    # expires_at se guarda naïve (UTC); lo comparamos como aware para evitar sorpresas.
    expires = inv.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < _now():
        inv.status = "expired"
        db.commit()
        return None
    return inv


def accept_invitation(db: Session, inv: Invitation) -> None:
    inv.status = "accepted"
    inv.accepted_at = _now()
    db.commit()


def build_invite_link(token: str) -> str:
    """Enlace que recibe el invitado (spec §9.2)."""
    return f"{settings.APP_PUBLIC_URL.rstrip('/')}/register?token={token}"


def email_already_registered(db: Session, email: str) -> bool:
    return db.query(User).filter(User.email == email).first() is not None
