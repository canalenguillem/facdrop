"""Servicio de Dropbox.

FASE 4: solo la prueba de conexión (consulta la cuenta actual con el token). La
subida de adjuntos (comprimidos en .zip por correo) llega en la Fase 6.
"""
import httpx

CURRENT_ACCOUNT_URL = "https://api.dropboxapi.com/2/users/get_current_account"


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
