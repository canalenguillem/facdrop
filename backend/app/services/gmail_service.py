"""Servicio de Gmail (IMAP, SOLO lectura).

La app nunca mueve ni borra correos: usa IMAP con `readonly=True` y `BODY.PEEK`
para no marcar nada como leído. Lee de las etiquetas vigiladas, saca metadatos y
descarga los adjuntos. La clasificación (RuleEngine) y la subida (Dropbox) viven
fuera de aquí.
"""
import email as emaillib
import imaplib
import re
from dataclasses import dataclass
from datetime import datetime
from email.header import decode_header
from email.message import Message
from email.utils import parsedate_to_datetime

IMAP_HOST = "imap.gmail.com"

# Carpetas IMAP internas de Gmail que no son etiquetas útiles para vigilar.
_SKIP_LABELS = {"[Gmail]", "INBOX"}

# Solo se descargan documentos; se ignoran imágenes (logos de firma, etc.).
ALLOWED_DOC_EXTENSIONS = {
    "pdf",
    "doc", "docx", "odt", "rtf", "txt",
    "xls", "xlsx", "xlsm", "xlsb", "ods", "csv", "tsv",
    "ppt", "pptx", "odp",
    "xml",
}


def _is_document(filename: str) -> bool:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in ALLOWED_DOC_EXTENSIONS

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


# =========================================================
# Lectura de correos y adjuntos (spec §10, §11)
# =========================================================
@dataclass
class Attachment:
    filename: str
    mime_type: str
    content: bytes

    @property
    def size(self) -> int:
        return len(self.content)


def _decode(value: str | None) -> str:
    """Decodifica cabeceras MIME (=?utf-8?...?=) a texto plano."""
    if not value:
        return ""
    parts = []
    for chunk, enc in decode_header(value):
        if isinstance(chunk, bytes):
            parts.append(chunk.decode(enc or "utf-8", errors="replace"))
        else:
            parts.append(chunk)
    return "".join(parts)


def _extract_attachments(msg: Message) -> list[Attachment]:
    """Adjuntos reales del mensaje (parte pura, sin IMAP)."""
    attachments: list[Attachment] = []
    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue
        if part.get("Content-Disposition") is None and not part.get_filename():
            continue
        filename = _decode(part.get_filename())
        if not filename:
            continue
        # Solo documentos: se descartan imágenes y otros ficheros no-documento.
        if not _is_document(filename):
            continue
        payload = part.get_payload(decode=True)
        if payload is None:
            continue
        attachments.append(
            Attachment(
                filename=filename,
                mime_type=part.get_content_type(),
                content=payload,
            )
        )
    return attachments


def _parse_date(msg: Message) -> datetime | None:
    """Fecha de recepción del correo (cabecera Date), o None si no se puede."""
    raw = msg.get("Date")
    if not raw:
        return None
    try:
        return parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        return None


def _email_meta(msg: Message, label_name: str) -> dict:
    """Metadatos que consume el RuleEngine (parte pura, sin IMAP)."""
    return {
        "id": _decode(msg.get("Message-ID")).strip(),
        "label_id": label_name,
        "from": _decode(msg.get("From")),
        "subject": _decode(msg.get("Subject")),
        "has_attachments": len(_extract_attachments(msg)) > 0,
        "date": _parse_date(msg),
    }


def _open(email: str, app_password: str) -> imaplib.IMAP4_SSL:
    imap = imaplib.IMAP4_SSL(IMAP_HOST, timeout=30)
    imap.login(email, app_password)
    return imap


# Meses en inglés para el formato de fecha de IMAP (independiente del locale).
_IMAP_MONTHS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


def _imap_date(d) -> str:
    """Formatea una fecha como la espera IMAP: DD-Mon-YYYY (ej: 01-Jan-2026)."""
    return f"{d.day:02d}-{_IMAP_MONTHS[d.month - 1]}-{d.year}"


def _search_criteria(since=None, until=None) -> list[str]:
    """Construye los criterios de búsqueda IMAP por fecha de recepción.

    SINCE incluye el día indicado; BEFORE es exclusivo, así que sumamos 1 día
    para que 'hasta' incluya el día completo.
    """
    from datetime import timedelta

    crit: list[str] = []
    if since is not None:
        crit += ["SINCE", _imap_date(since)]
    if until is not None:
        crit += ["BEFORE", _imap_date(until + timedelta(days=1))]
    return crit or ["ALL"]


def fetch_emails(
    email: str,
    app_password: str,
    label_name: str,
    limit: int = 200,
    since=None,
    until=None,
) -> list[dict]:
    """Lee (readonly) los correos de una etiqueta y devuelve sus metadatos.

    Filtra por fecha de recepción en el servidor (SINCE/BEFORE) para no traer
    años de historial. No marca nada como leído (SELECT readonly + BODY.PEEK).
    """
    imap = _open(email, app_password)
    try:
        # El nombre de la etiqueta puede llevar espacios: se entrecomilla.
        status, _ = imap.select(f'"{label_name}"', readonly=True)
        if status != "OK":
            return []
        typ, data = imap.search(None, *_search_criteria(since, until))
        if typ != "OK" or not data or not data[0]:
            return []
        ids = data[0].split()[-limit:]
        emails: list[dict] = []
        for num in ids:
            typ, msg_data = imap.fetch(num, "(BODY.PEEK[])")
            if typ != "OK" or not msg_data or not msg_data[0]:
                continue
            raw = msg_data[0][1]
            emails.append(_email_meta(emaillib.message_from_bytes(raw), label_name))
        return emails
    finally:
        try:
            imap.logout()
        except Exception:  # noqa: BLE001
            pass


def download_attachments(
    email: str, app_password: str, label_name: str, message_id: str
) -> list[Attachment]:
    """Descarga los adjuntos de un correo concreto (por Message-ID), readonly."""
    imap = _open(email, app_password)
    try:
        status, _ = imap.select(f'"{label_name}"', readonly=True)
        if status != "OK":
            return []
        typ, data = imap.search(None, "HEADER", "Message-ID", message_id)
        if typ != "OK" or not data or not data[0]:
            return []
        num = data[0].split()[-1]
        typ, msg_data = imap.fetch(num, "(BODY.PEEK[])")
        if typ != "OK" or not msg_data or not msg_data[0]:
            return []
        raw = msg_data[0][1]
        return _extract_attachments(emaillib.message_from_bytes(raw))
    finally:
        try:
            imap.logout()
        except Exception:  # noqa: BLE001
            pass
