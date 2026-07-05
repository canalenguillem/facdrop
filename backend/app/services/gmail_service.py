"""Servicio de Gmail.

FASE 4: solo la prueba de conexión (login IMAP con la App Password). La lectura
de correos de las etiquetas vigiladas y la descarga de adjuntos llegan en la
Fase 6.
"""
import imaplib

IMAP_HOST = "imap.gmail.com"


def test_connection(email: str, app_password: str) -> tuple[bool, str | None]:
    """Prueba la App Password haciendo login IMAP. (True, None) si conecta."""
    try:
        with imaplib.IMAP4_SSL(IMAP_HOST, timeout=15) as imap:
            imap.login(email, app_password)
        return True, None
    except imaplib.IMAP4.error:
        return False, "Login rechazado: revisa el email y la App Password."
    except Exception as exc:  # noqa: BLE001
        return False, f"No se pudo conectar con Gmail: {exc}"
