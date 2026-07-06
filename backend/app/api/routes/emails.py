"""Router de correos: procesado e historial (spec §8.7, §10, §11).

Orquesta el flujo completo por usuario:
  etiquetas vigiladas → fetch (readonly) → RuleEngine → descargar adjuntos →
  subir cada uno a la carpeta Dropbox de la regla → registrar en email_logs
  (procesado / sin_regla / error) + metadatos en MongoDB.

La app NUNCA mueve ni borra correos en Gmail.
"""
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.middleware import get_current_user
from app.database import get_db, mongo_db
from app.models.email_log import EmailLog
from app.models.gmail_label import GmailLabel
from app.models.rule import Rule
from app.models.user import User
from app.schemas.email import EmailLogOut, EmailStats, ProcessResult
from app.services import dropbox_service, gmail_service
from app.services.rule_engine import RuleEngine
from app.utils.logger import get_logger
from app.utils.security import encryptor

router = APIRouter(prefix="/emails", tags=["emails"])
logger = get_logger(__name__)


# =========================================================
# Orquestación (importable y testeable con mocks)
# =========================================================
def _process_single_email(
    db: Session,
    user: User,
    meta: dict,
    rules: list,
    engine: RuleEngine,
    gmail_email: str,
    gmail_pw: str,
    dropbox_token: str | None,
    counts: dict,
) -> None:
    rule = engine.find_matching_rule(meta, rules)

    log = EmailLog(
        user_id=user.id,
        gmail_message_id=meta["id"],
        from_email=meta.get("from"),
        subject=meta.get("subject"),
        source_label=meta.get("label_id"),
    )

    # Ninguna regla coincide → no se toca el correo, solo se registra.
    if not rule:
        log.status = "sin_regla"
        log.doc_type = "ignorado"
        db.add(log)
        db.commit()
        counts["sin_regla"] += 1
        return

    try:
        if not dropbox_token:
            raise RuntimeError("El usuario no tiene credencial de Dropbox configurada.")

        attachments = gmail_service.download_attachments(
            gmail_email, gmail_pw, meta["label_id"], meta["id"]
        )
        folder = rule.dropbox_folder

        # Carpeta destino: opcionalmente en subcarpetas por fecha de recepción
        # (AAAA/MM/DD). Si el correo no trae fecha, se usa la de procesado.
        base_path = folder.dropbox_path.rstrip("/")
        if folder.organize_by_date:
            email_date = meta.get("date") or datetime.now(timezone.utc)
            base_path = f"{base_path}/{email_date.strftime('%Y/%m/%d')}"

        uploaded: list[str] = []
        mongo_atts: list[dict] = []
        for att in attachments:
            path = f"{base_path}/{att.filename}"
            final_path = dropbox_service.upload(dropbox_token, path, att.content)
            uploaded.append(final_path)
            mongo_atts.append(
                {
                    "filename": att.filename,
                    "mime_type": att.mime_type,
                    "size": att.size,
                    "dropbox_path": final_path,
                }
            )

        log.status = "procesado"
        log.doc_type = rule.doc_type
        log.rule_applied_id = rule.id
        log.dropbox_folder_id = folder.id
        log.dropbox_file_path = uploaded[0] if uploaded else None
        db.add(log)
        db.commit()

        # Metadatos de adjuntos en MongoDB (spec §7.2)
        mongo_db.email_attachments.insert_one(
            {
                "user_id": int(user.id),
                "gmail_message_id": meta["id"],
                "attachments": mongo_atts,
                "created_at": datetime.now(timezone.utc),
            }
        )
        counts["procesado"] += 1

    except Exception as exc:  # noqa: BLE001
        db.rollback()
        logger.error("Error procesando %s: %s", meta.get("id"), exc)
        log.status = "error"
        log.doc_type = rule.doc_type
        log.rule_applied_id = rule.id
        log.error_message = str(exc)[:1000]
        db.add(log)
        db.commit()
        counts["error"] += 1


def process_user_emails(db: Session, user: User, since=None, until=None) -> dict:
    """Procesa los correos pendientes de las etiquetas vigiladas del usuario.

    `since`/`until` (date) acotan por fecha de recepción para no procesar años
    de historial de golpe.
    """
    counts = {"total": 0, "procesado": 0, "sin_regla": 0, "error": 0, "skipped": 0}

    gmail_email = user.gmail_user_email
    gmail_pw = encryptor.decrypt(user.gmail_app_password)
    try:
        dropbox_token = dropbox_service.get_user_access_token(user)
    except RuntimeError as exc:
        logger.error("No se pudo obtener el token de Dropbox: %s", exc)
        dropbox_token = None

    labels = (
        db.query(GmailLabel)
        .filter(GmailLabel.user_id == user.id, GmailLabel.is_active == True)  # noqa: E712
        .all()
    )
    rules = (
        db.query(Rule)
        .filter(Rule.user_id == user.id, Rule.is_active == True)  # noqa: E712
        .all()
    )
    engine = RuleEngine()

    for label in labels:
        try:
            emails = gmail_service.fetch_emails(
                gmail_email, gmail_pw, label.gmail_label_name, since=since, until=until
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("No se pudo leer la etiqueta %s: %s", label.gmail_label_name, exc)
            continue

        for meta in emails:
            counts["total"] += 1
            mid = meta.get("id")
            if not mid:
                continue
            already = (
                db.query(EmailLog).filter(EmailLog.gmail_message_id == mid).first()
            )
            if already:
                counts["skipped"] += 1
                continue
            _process_single_email(
                db, user, meta, rules, engine, gmail_email, gmail_pw, dropbox_token, counts
            )

    return counts


# =========================================================
# Endpoints (spec §8.7)
# =========================================================
def _require_gmail(user: User) -> None:
    if not user.gmail_app_password or not user.gmail_user_email:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Configura primero tu credencial de Gmail en el perfil.",
        )


@router.get("", response_model=list[EmailLogOut])
def list_emails(
    db: Session = Depends(get_db), current: User = Depends(get_current_user)
):
    return (
        db.query(EmailLog)
        .filter(EmailLog.user_id == current.id)
        .order_by(EmailLog.processed_at.desc())
        .all()
    )


@router.get("/stats", response_model=EmailStats)
def email_stats(db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    rows = (
        db.query(EmailLog.status, func.count(EmailLog.id))
        .filter(EmailLog.user_id == current.id)
        .group_by(EmailLog.status)
        .all()
    )
    by_status = {status_: count for status_, count in rows}
    return EmailStats(
        total=sum(by_status.values()),
        procesado=by_status.get("procesado", 0),
        sin_regla=by_status.get("sin_regla", 0),
        error=by_status.get("error", 0),
    )


@router.get("/{log_id}", response_model=EmailLogOut)
def get_email(
    log_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)
):
    log = (
        db.query(EmailLog)
        .filter(EmailLog.id == log_id, EmailLog.user_id == current.id)
        .first()
    )
    if not log:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Correo no encontrado")
    return log


@router.post("/process", response_model=ProcessResult)
def process_emails(
    since: date | None = None,
    until: date | None = None,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Procesa los correos pendientes de las etiquetas vigiladas (spec §10).

    Parámetros opcionales `since`/`until` (YYYY-MM-DD) acotan por fecha de
    recepción, para no procesar años de historial de golpe.
    """
    _require_gmail(current)
    counts = process_user_emails(db, current, since=since, until=until)
    return ProcessResult(**counts)


@router.post("/{log_id}/reprocess", response_model=ProcessResult)
def reprocess_email(
    log_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)
):
    """Reprocesa un correo concreto: borra su registro y vuelve a procesarlo."""
    _require_gmail(current)
    log = (
        db.query(EmailLog)
        .filter(EmailLog.id == log_id, EmailLog.user_id == current.id)
        .first()
    )
    if not log:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Correo no encontrado")
    mid = log.gmail_message_id
    mongo_db.email_attachments.delete_many({"gmail_message_id": mid, "user_id": int(current.id)})
    db.delete(log)
    db.commit()
    counts = process_user_emails(db, current)
    return ProcessResult(**counts)
