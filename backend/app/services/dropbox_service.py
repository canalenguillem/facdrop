"""Servicio de Dropbox.

FASE 4: solo la prueba de conexión (consulta la cuenta actual con el token). La
subida de adjuntos (comprimidos en .zip por correo) llega en la Fase 6.
"""
import httpx

CURRENT_ACCOUNT_URL = "https://api.dropboxapi.com/2/users/get_current_account"
LIST_FOLDER_URL = "https://api.dropboxapi.com/2/files/list_folder"


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
