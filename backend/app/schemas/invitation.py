"""Schemas Pydantic de invitaciones y registro por token (spec §9)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- Admin: crear/listar invitaciones ---
class InvitationCreate(BaseModel):
    email: EmailStr
    role: str = "user"  # 'user' | 'admin'


class InvitationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    role: str
    status: str
    expires_at: datetime
    accepted_at: datetime | None = None
    created_at: datetime
    # Enlace de alta (solo para el admin, útil sin SMTP para copiarlo a mano).
    invite_link: str | None = None
    # True/False si se acaba de intentar enviar por email; None si no aplica.
    email_sent: bool | None = None


# --- Público: validar token y registrarse ---
class InviteValidateOut(BaseModel):
    """Respuesta de GET /api/auth/invite/{token}: el email queda fijado."""
    email: EmailStr
    role: str
    expires_at: datetime


class RegisterInvite(BaseModel):
    """POST /api/auth/register: el email NO se acepta aquí (lo fija la invitación)."""
    token: str
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=128)
