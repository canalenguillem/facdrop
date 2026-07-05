"""Servicio de Dropbox.

Prueba de conexión, navegación de carpetas y subida de adjuntos. Por decisión de
producto, los adjuntos de un correo se suben COMPRIMIDOS en un único .zip por
correo (ver build_email_zip / upload_email_zip).
"""
import io
import json
import re
import zipfile

import httpx

CURRENT_ACCOUNT_URL = "https://api.dropboxapi.com/2/users/get_current_account"
LIST_FOLDER_URL = "https://api.dropboxapi.com/2/files/list_folder"
UPLOAD_URL = "https://content.dropboxapi.com/2/files/upload"


def test_connection(access_token: str) -> tuple[bool, str | None]:
    """Prueba el Access Token consultando la cuenta. (True, None) si es válido."""
    try:
        resp = httpx.post(
            CURRENT_ACCOUNT_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=15,
        )
        if resp.status_code == 200:
            return True, None
        if resp.status_code == 401:
            return False, "Token inválido o expirado."
        return False, f"Dropbox respondió {resp.status_code}: {resp.text[:200]}"
    except Exception as exc:  # noqa: BLE001
        return False, f"No se pudo conectar con Dropbox: {exc}"


def list_folders(access_token: str, path: str = "") -> list[dict]:
    """Lista las carpetas de Dropbox dentro de `path` ("" = raíz).

    Devuelve solo carpetas: [{name, path}]. Lanza RuntimeError si el token no es
    válido o la API responde con error, para que el endpoint lo traduzca a HTTP.
    """
    # La API exige "" para la raíz; cualquier otra ruta debe empezar por "/".
    api_path = "" if path in ("", "/") else path
    resp = httpx.post(
        LIST_FOLDER_URL,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        json={"path": api_path},
        timeout=20,
    )
    if resp.status_code == 401:
        raise RuntimeError("Token de Dropbox inválido o expirado.")
    if resp.status_code != 200:
        raise RuntimeError(f"Dropbox respondió {resp.status_code}: {resp.text[:200]}")

    entries = resp.json().get("entries", [])
    return [
        {"name": e["name"], "path": e["path_display"]}
        for e in entries
        if e.get(".tag") == "folder"
    ]


# =========================================================
# Subida de adjuntos (spec §11) — .zip por correo (decisión de producto)
# =========================================================
_SAFE_NAME_RE = re.compile(r"[^\w.\- ]+")


def safe_filename(name: str, fallback: str = "adjuntos") -> str:
    """Sanea un texto para usarlo como nombre de fichero."""
    cleaned = _SAFE_NAME_RE.sub("", name).strip().strip(".")
    return cleaned[:120] or fallback


def build_email_zip(attachments: list) -> bytes:
    """Empaqueta los adjuntos de UN correo en un .zip (en memoria).

    `attachments` es una lista de objetos con .filename y .content (bytes)
    (gmail_service.Attachment). Si hay nombres repetidos, se desambiguan.
    """
    buffer = io.BytesIO()
    seen: dict[str, int] = {}
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for att in attachments:
            name = att.filename or "adjunto"
            if name in seen:
                seen[name] += 1
                stem, _, ext = name.rpartition(".")
                name = f"{stem}_{seen[name]}.{ext}" if ext else f"{name}_{seen[name]}"
            else:
                seen[name] = 0
            zf.writestr(name, att.content)
    return buffer.getvalue()


def _dropbox_upload(access_token: str, dropbox_path: str, content: bytes) -> str:
    """Sube un fichero a Dropbox. Devuelve la ruta final. Lanza RuntimeError."""
    api_arg = {
        "path": dropbox_path,
        "mode": "add",
        "autorename": True,
        "mute": False,
    }
    resp = httpx.post(
        UPLOAD_URL,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Dropbox-API-Arg": json.dumps(api_arg),
            "Content-Type": "application/octet-stream",
        },
        content=content,
        timeout=60,
    )
    if resp.status_code == 401:
        raise RuntimeError("Token de Dropbox inválido o expirado.")
    if resp.status_code != 200:
        raise RuntimeError(f"Dropbox respondió {resp.status_code}: {resp.text[:200]}")
    return resp.json().get("path_display", dropbox_path)


def upload_email_zip(
    access_token: str, folder_path: str, zip_basename: str, attachments: list
) -> str:
    """Comprime los adjuntos del correo y sube el .zip a la carpeta destino.

    Devuelve la ruta final en Dropbox. `folder_path` es la ruta de la carpeta de
    la regla (ej: /Empresa/Facturas/Enero2026).
    """
    zip_bytes = build_email_zip(attachments)
    filename = f"{safe_filename(zip_basename)}.zip"
    full_path = f"{folder_path.rstrip('/')}/{filename}"
    return _dropbox_upload(access_token, full_path, zip_bytes)
