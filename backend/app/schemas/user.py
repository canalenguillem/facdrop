"""Schemas Pydantic de usuario y autenticación."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- Auth ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# --- Usuario ---
class UserOut(BaseModel):
    """Datos del usuario que SÍ se exponen (nunca credenciales en claro)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str
    is_active: bool
    is_admin: bool
    role: str
    gmail_connected: bool
    dropbox_connected: bool
    created_at: datetime


class UserUpdateMe(BaseModel):
    """Campos que el propio usuario puede cambiar de su perfil."""
    username: str | None = None


class UserAdminUpdate(BaseModel):
    """Campos que un admin puede cambiar de otro usuario (activar/rol)."""
    is_active: bool | None = None
    role: str | None = None


# --- Credenciales de servicio (spec §8.3) ---
class GmailCredentialIn(BaseModel):
    gmail_user_email: EmailStr
    gmail_app_password: str = Field(min_length=1)


class DropboxCredentialIn(BaseModel):
    dropbox_access_token: str = Field(min_length=1)


class CredentialStatus(BaseModel):
    """Estado de las credenciales (NUNCA el valor en claro)."""
    model_config = ConfigDict(from_attributes=True)

    gmail_connected: bool
    gmail_user_email: str | None = None
    gmail_last_tested: datetime | None = None
    gmail_test_status: str | None = None

    dropbox_connected: bool
    dropbox_last_tested: datetime | None = None
    dropbox_test_status: str | None = None


class CredentialTestResult(BaseModel):
    service: str                 # 'gmail' | 'dropbox'
    status: str                  # 'success' | 'failed'
    error_message: str | None = None
