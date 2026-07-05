"""Servicio de Gmail.

FASE 4: solo la prueba de conexión (login IMAP con la App Password). La lectura
de correos de las etiquetas vigiladas y la descarga de adjuntos llegan en la
Fase 6.
"""
import imaplib
import re

IMAP_HOST = "imap.gmail.com"

# Carpetas IMAP internas de Gmail que no son etiquetas útiles para vigilar.
_SKIP_LABELS = {"[Gmail]", "INBOX"}

# Formato de cada línea de IMAP LIST: (flags) "sep" "nombre"
_LIST_RE = re.compile(r'\((?P<flags>[^)]*)\)\s+"[^"]*"\s+(?P<name>.+)$')


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


def list_labels(email: str, app_password: str) -> list[dict]:
    """Lista las etiquetas de Gmail (vía IMAP LIST). SOLO lectura.

    Gmail expone cada etiqueta como una "carpeta" IMAP. No hay un ID separado,
    así que usamos el nombre como id y como nombre. Ignora carpetas internas y
    las marcadas \\Noselect.
    """
    labels: list[dict] = []
    with imaplib.IMAP4_SSL(IMAP_HOST, timeout=20) as imap:
        imap.login(email, app_password)
        typ, data = imap.list()
        if typ != "OK":
            return []
        for raw in data:
            line = raw.decode() if isinstance(raw, bytes) else str(raw)
            m = _LIST_RE.match(line)
            if not m:
                continue
            if "\\Noselect" in m.group("flags"):
                continue
            name = m.group("name").strip().strip('"')
            if name in _SKIP_LABELS or name.startswith("[Gmail]"):
                continue
            labels.append({"gmail_label_id": name, "gmail_label_name": name})
    return labels
