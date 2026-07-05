"""Schemas Pydantic de etiquetas de Gmail vigiladas (spec §8.4)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GmailLabelAvailable(BaseModel):
    """Etiqueta real de Gmail traída por sync (aún no necesariamente vigilada)."""
    gmail_label_id: str
    gmail_label_name: str


class WatchedLabelCreate(BaseModel):
    """Activar una etiqueta para vigilar."""
    gmail_label_id: str
    gmail_label_name: str


class WatchedLabelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    gmail_label_id: str
    gmail_label_name: str
    is_active: bool
    created_at: datetime
