"""Router de etiquetas de Gmail vigiladas (spec §8.4).

La app SOLO lee de las etiquetas que el usuario marca aquí. `sync`/`available`
consultan Gmail (IMAP) con la App Password guardada; el resto son CRUD local.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.middleware import get_current_user
from app.database import get_db
from app.models.gmail_label import GmailLabel
from app.models.rule import Rule
from app.models.user import User
from app.schemas.label import GmailLabelAvailable, WatchedLabelCreate, WatchedLabelOut
from app.services import gmail_service
from app.utils.security import encryptor

router = APIRouter(prefix="/labels", tags=["labels"])


def _require_gmail(current: User) -> tuple[str, str]:
    if not current.gmail_app_password or not current.gmail_user_email:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Configura primero tu credencial de Gmail en el perfil.",
        )
    return current.gmail_user_email, encryptor.decrypt(current.gmail_app_password)


@router.post("/gmail/sync", response_model=list[GmailLabelAvailable])
def sync_gmail_labels(current: User = Depends(get_current_user)):
    """Trae las etiquetas reales de la cuenta de Gmail (solo lectura)."""
    email, password = _require_gmail(current)
    try:
        return gmail_service.list_labels(email, password)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Error consultando Gmail: {exc}")


@router.get("/gmail/available", response_model=list[GmailLabelAvailable])
def available_gmail_labels(current: User = Depends(get_current_user)):
    """Alias de sync: lista todas las etiquetas de Gmail del usuario."""
    email, password = _require_gmail(current)
    try:
        return gmail_service.list_labels(email, password)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Error consultando Gmail: {exc}")


@router.get("", response_model=list[WatchedLabelOut])
def list_watched(db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    return (
        db.query(GmailLabel)
        .filter(GmailLabel.user_id == current.id)
        .order_by(GmailLabel.created_at)
        .all()
    )


@router.post("", response_model=WatchedLabelOut, status_code=status.HTTP_201_CREATED)
def watch_label(
    data: WatchedLabelCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    exists = (
        db.query(GmailLabel)
        .filter(
            GmailLabel.user_id == current.id,
            GmailLabel.gmail_label_id == data.gmail_label_id,
        )
        .first()
    )
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Esa etiqueta ya está vigilada")
    label = GmailLabel(
        user_id=current.id,
        gmail_label_id=data.gmail_label_id,
        gmail_label_name=data.gmail_label_name,
        is_active=True,
    )
    db.add(label)
    db.commit()
    db.refresh(label)
    return label


def _get_own_label(db: Session, label_id: int, user: User) -> GmailLabel:
    label = (
        db.query(GmailLabel)
        .filter(GmailLabel.id == label_id, GmailLabel.user_id == user.id)
        .first()
    )
    if not label:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Etiqueta no encontrada")
    return label


@router.delete("/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
def unwatch_label(
    label_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)
):
    label = _get_own_label(db, label_id, current)
    n_rules = db.query(Rule).filter(Rule.source_label_id == label.id).count()
    if n_rules:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"No puedes dejar de vigilar esta etiqueta: la usan {n_rules} regla(s). "
            "Elimina esas reglas primero.",
        )
    db.delete(label)
    db.commit()


@router.put("/{label_id}/toggle", response_model=WatchedLabelOut)
def toggle_label(
    label_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)
):
    label = _get_own_label(db, label_id, current)
    label.is_active = not label.is_active
    db.commit()
    db.refresh(label)
    return label
