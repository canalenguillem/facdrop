"""Router de integraciones (spec §8.8): estado de Gmail / Dropbox / N8N."""
import httpx
from fastapi import APIRouter, Depends

from app.api.middleware import get_current_user
from app.models.user import User

router = APIRouter(prefix="/integrations", tags=["integrations"])

# Dentro de la red Docker el backend alcanza n8n por su nombre de servicio.
N8N_HEALTH_URL = "http://n8n:5678/healthz"


@router.get("/status")
def integrations_status(current: User = Depends(get_current_user)):
    """Estado de las integraciones del usuario + disponibilidad de N8N."""
    n8n_up = False
    try:
        n8n_up = httpx.get(N8N_HEALTH_URL, timeout=5).status_code == 200
    except Exception:  # noqa: BLE001
        n8n_up = False

    return {
        "gmail": {
            "connected": current.gmail_connected,
            "last_tested": current.gmail_last_tested,
            "test_status": current.gmail_test_status,
        },
        "dropbox": {
            "connected": current.dropbox_connected,
            "last_tested": current.dropbox_last_tested,
            "test_status": current.dropbox_test_status,
        },
        "n8n": {"available": n8n_up},
    }
