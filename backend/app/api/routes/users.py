"""Router de usuarios y perfil (spec §8.3).

En esta fase: datos del usuario actual (/me) y gestión de usuarios por admin.
Los endpoints de credenciales Gmail/Dropbox (/me/credentials/*) llegan en la
Fase 4 (encriptación).
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.middleware import get_current_user, require_admin
from app.database import get_db
from app.models.credential_log import CredentialLog
from app.models.user import User
from app.schemas.user import (
    CredentialStatus,
    CredentialTestResult,
    DropboxCredentialIn,
    GmailCredentialIn,
    UserAdminUpdate,
    UserOut,
    UserUpdateMe,
)
from app.services import dropbox_service, gmail_service
from app.utils.security import encryptor

router = APIRouter(prefix="/users", tags=["users"])


def _log_credential(
    db: Session,
    user_id: int,
    service: str,
    action: str,
    test_result: str | None = None,
    error: str | None = None,
) -> None:
    """Auditoría de credenciales (spec §13.2): registra cada cambio/prueba."""
    db.add(
        CredentialLog(
            user_id=user_id,
            service=service,
            action=action,
            test_result=test_result,
            error_message=error,
        )
    )


@router.get("/me", response_model=UserOut)
def get_me(current: User = Depends(get_current_user)):
    return current


@router.put("/me", response_model=UserOut)
def update_me(
    data: UserUpdateMe,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if data.username is not None:
        clash = (
            db.query(User)
            .filter(User.username == data.username, User.id != current.id)
            .first()
        )
        if clash:
            raise HTTPException(status.HTTP_409_CONFLICT, "Ese username ya está en uso")
        current.username = data.username
    db.commit()
    db.refresh(current)
    return current


# =========================================================
# Credenciales de servicio (Gmail / Dropbox) — spec §8.3, §13.2
# Se guardan ENCRIPTADAS (Fernet). El frontend nunca recibe el valor en claro.
# =========================================================
def _now():
    return datetime.now(timezone.utc)


@router.get("/me/credentials", response_model=CredentialStatus)
def get_credentials_status(current: User = Depends(get_current_user)):
    current.dropbox_oauth_available = dropbox_service.oauth_enabled()
    return current


@router.put("/me/credentials/gmail", response_model=CredentialStatus)
def set_gmail_credential(
    data: GmailCredentialIn,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    action = "updated" if current.gmail_app_password else "added"
    current.gmail_app_password = encryptor.encrypt(data.gmail_app_password)
    current.gmail_user_email = data.gmail_user_email
    current.gmail_connected = True
    current.gmail_connected_at = _now()
    _log_credential(db, current.id, "gmail", action)
    db.commit()
    db.refresh(current)
    return current


@router.put("/me/credentials/dropbox", response_model=CredentialStatus)
def set_dropbox_credential(
    data: DropboxCredentialIn,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    action = "updated" if current.dropbox_access_token else "added"
    current.dropbox_access_token = encryptor.encrypt(data.dropbox_access_token)
    current.dropbox_connected = True
    current.dropbox_connected_at = _now()
    _log_credential(db, current.id, "dropbox", action)
    db.commit()
    db.refresh(current)
    return current


@router.post("/me/credentials/test/gmail", response_model=CredentialTestResult)
def test_gmail_credential(
    db: Session = Depends(get_db), current: User = Depends(get_current_user)
):
    if not current.gmail_app_password or not current.gmail_user_email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No hay credencial de Gmail guardada")
    ok, err = gmail_service.test_connection(
        current.gmail_user_email, encryptor.decrypt(current.gmail_app_password)
    )
    result = "success" if ok else "failed"
    current.gmail_last_tested = _now()
    current.gmail_test_status = result
    _log_credential(db, current.id, "gmail", "tested", test_result=result, error=err)
    db.commit()
    return CredentialTestResult(service="gmail", status=result, error_message=err)


@router.post("/me/credentials/test/dropbox", response_model=CredentialTestResult)
def test_dropbox_credential(
    db: Session = Depends(get_db), current: User = Depends(get_current_user)
):
    if not dropbox_service.user_has_dropbox(current):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No hay Dropbox conectado")
    try:
        token = dropbox_service.get_user_access_token(current)
        ok, err = dropbox_service.test_connection(token)
    except RuntimeError as exc:
        ok, err = False, str(exc)
    result = "success" if ok else "failed"
    current.dropbox_last_tested = _now()
    current.dropbox_test_status = result
    _log_credential(db, current.id, "dropbox", "tested", test_result=result, error=err)
    db.commit()
    return CredentialTestResult(service="dropbox", status=result, error_message=err)


@router.delete("/me/credentials/gmail", response_model=CredentialStatus)
def delete_gmail_credential(
    db: Session = Depends(get_db), current: User = Depends(get_current_user)
):
    current.gmail_app_password = None
    current.gmail_user_email = None
    current.gmail_connected = False
    current.gmail_connected_at = None
    current.gmail_last_tested = None
    current.gmail_test_status = None
    _log_credential(db, current.id, "gmail", "removed")
    db.commit()
    db.refresh(current)
    return current


@router.delete("/me/credentials/dropbox", response_model=CredentialStatus)
def delete_dropbox_credential(
    db: Session = Depends(get_db), current: User = Depends(get_current_user)
):
    current.dropbox_access_token = None
    current.dropbox_refresh_token = None
    current.dropbox_connected = False
    current.dropbox_connected_at = None
    current.dropbox_last_tested = None
    current.dropbox_test_status = None
    _log_credential(db, current.id, "dropbox", "removed")
    db.commit()
    db.refresh(current)
    return current


# --- Dropbox OAuth (acceso permanente vía refresh token) ---
@router.get("/me/credentials/dropbox/authorize-url")
def dropbox_authorize_url(
    redirect_uri: str, current: User = Depends(get_current_user)
):
    """Devuelve la URL a la que redirigir para autorizar Dropbox (OAuth)."""
    if not dropbox_service.oauth_enabled():
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "OAuth de Dropbox no configurado en el servidor (DROPBOX_APP_KEY/SECRET).",
        )
    return {"url": dropbox_service.build_authorize_url(redirect_uri)}


@router.post("/me/credentials/dropbox/connect", response_model=CredentialStatus)
def dropbox_oauth_connect(
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Canjea el 'code' de OAuth por un refresh token y lo guarda (permanente)."""
    code = payload.get("code")
    redirect_uri = payload.get("redirect_uri")
    if not code or not redirect_uri:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Faltan 'code' o 'redirect_uri'")
    try:
        refresh = dropbox_service.exchange_code(code, redirect_uri)
    except RuntimeError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))

    action = "updated" if current.dropbox_refresh_token else "added"
    current.dropbox_refresh_token = encryptor.encrypt(refresh)
    current.dropbox_access_token = None  # se usa el refresh token de ahora en adelante
    current.dropbox_connected = True
    current.dropbox_connected_at = _now()
    _log_credential(db, current.id, "dropbox", action)
    db.commit()
    db.refresh(current)
    return current


@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(User).order_by(User.created_at).all()


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    data: UserAdminUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.role is not None:
        user.role = data.role
        user.is_admin = data.role == "admin"
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    if user_id == admin.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No puedes eliminarte a ti mismo")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    db.delete(user)
    db.commit()
