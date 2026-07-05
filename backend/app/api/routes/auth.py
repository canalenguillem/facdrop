"""Router de autenticación (spec §8.1, §9.4).

Público (sin JWT): login, refresh, logout, validar invitación y registro.
No hay registro abierto: /register exige un token de invitación válido.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.middleware import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.invitation import InviteValidateOut, RegisterInvite
from app.schemas.user import LoginRequest, RefreshRequest, Token
from app.services import auth_service, invitation_service
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate(db, data.email, data.password)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciales inválidas")
    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=Token)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_token(data.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token inválido")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario no válido")
    return Token(access_token=create_access_token(user.id))


@router.post("/logout")
def logout(current: User = Depends(get_current_user)):
    # JWT es stateless: el cliente descarta el token. (Blocklist en Redis = futuro.)
    return {"detail": "Sesión cerrada"}


@router.get("/invite/{token}", response_model=InviteValidateOut)
def validate_invite(token: str, db: Session = Depends(get_db)):
    """(Público) Valida el token de invitación. El email queda fijado."""
    inv = invitation_service.get_valid_invitation(db, token)
    if not inv:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invitación inválida o caducada")
    return InviteValidateOut(email=inv.email, role=inv.role, expires_at=inv.expires_at)


@router.post("/register", response_model=Token)
def register(data: RegisterInvite, db: Session = Depends(get_db)):
    """(Público) Alta con token de invitación (spec §9.4)."""
    inv = invitation_service.get_valid_invitation(db, data.token)
    if not inv:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invitación inválida o caducada")

    if invitation_service.email_already_registered(db, inv.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ese email ya tiene cuenta")

    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Ese username ya está en uso")

    user = User(
        email=inv.email,  # fijado por la invitación
        username=data.username,
        hashed_password=hash_password(data.password),
        role=inv.role,
        is_admin=(inv.role == "admin"),
        is_active=True,
    )
    db.add(user)
    invitation_service.accept_invitation(db, inv)  # marca 'accepted' + commit
    db.refresh(user)

    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )
