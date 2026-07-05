"""Servicio de email: envío SMTP de invitaciones (spec §4, §8.2).

Resiliente: si SMTP no está configurado (SMTP_HOST vacío), en vez de fallar se
registra el enlace en el log para poder copiarlo en desarrollo.
"""
import smtplib
from email.message import EmailMessage

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def send_invitation_email(to_email: str, invite_link: str) -> bool:
    """Envía el email con el enlace de invitación. Devuelve True si se envió."""
    if not settings.SMTP_HOST:
        logger.warning(
            "SMTP no configurado. Enlace de invitación para %s: %s",
            to_email,
            invite_link,
        )
        return False

    msg = EmailMessage()
    msg["Subject"] = "Invitación a Fracdrop"
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email
    msg.set_content(
        "Te han invitado a Fracdrop.\n\n"
        f"Crea tu cuenta con este enlace:\n{invite_link}\n\n"
        f"El enlace caduca en {settings.INVITATION_EXPIRE_DAYS} días."
    )

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
            smtp.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.send_message(msg)
        logger.info("Invitación enviada a %s", to_email)
        return True
    except Exception as exc:  # noqa: BLE001  (no queremos que un fallo SMTP tumbe el endpoint)
        logger.error("Fallo enviando invitación a %s: %s", to_email, exc)
        logger.warning("Enlace de invitación para %s: %s", to_email, invite_link)
        return False
