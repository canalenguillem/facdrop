"""Schemas Pydantic de carpetas de Dropbox (spec §8.6)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FolderCreate(BaseModel):
    name: str
    dropbox_path: str
    doc_type: str  # 'factura' | 'albaran' | 'otros'
    organize_by_date: bool = False


class FolderUpdate(BaseModel):
    name: str | None = None
    dropbox_path: str | None = None
    doc_type: str | None = None
    organize_by_date: bool | None = None


class FolderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    dropbox_path: str
    doc_type: str
    organize_by_date: bool
    created_at: datetime


class DropboxEntry(BaseModel):
    """Carpeta existente en Dropbox (para el navegador de carpetas)."""
    name: str
    path: str
