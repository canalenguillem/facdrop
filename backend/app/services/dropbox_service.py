"""Servicio de Dropbox.

Prueba de conexión, navegación de carpetas y subida de adjuntos. Cada adjunto se
sube como fichero independiente a la carpeta de la regla (spec §11).
"""
import json

import httpx

CURRENT_ACCOUNT_URL = "https://api.dropboxapi.com/2/users/get_current_account"
LIST_FOLDER_URL = "https://api.dropboxapi.com/2/files/list_folder"
CREATE_FOLDER_URL = "https://api.dropboxapi.com/2/files/create_folder_v2"
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


def create_folder(access_token: str, path: str) -> None:
    """Crea una carpeta en Dropbox (idempotente).

    Dropbox crea también las carpetas padre. Si ya existe (409 conflict) se
    considera OK. Lanza RuntimeError en otros errores.
    """
    resp = httpx.post(
        CREATE_FOLDER_URL,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        json={"path": path, "autorename": False},
        timeout=20,
    )
    if resp.status_code == 200:
        return
    if resp.status_code == 409:
        # Ya existe (u otro conflicto de ruta): idempotente, lo damos por bueno.
        return
    if resp.status_code == 401:
        raise RuntimeError("Token de Dropbox inválido o expirado.")
    raise RuntimeError(f"Dropbox respondió {resp.status_code}: {resp.text[:200]}")


# =========================================================
# Subida de adjuntos (spec §11) — un fichero por adjunto
# =========================================================
def upload(access_token: str, dropbox_path: str, content: bytes) -> str:
    """Sube un fichero a Dropbox en `dropbox_path`. Devuelve la ruta final.

    Lanza RuntimeError si el token no es válido o la API responde con error.
    """
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
