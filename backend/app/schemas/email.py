"""Schemas Pydantic del historial de correos procesados (spec §8.7)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EmailLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    gmail_message_id: str
    from_email: str | None = None
    subject: str | None = None
    source_label: str | None = None
    doc_type: str | None = None
    status: str | None = None
    rule_applied_id: int | None = None
    dropbox_folder_id: int | None = None
    dropbox_file_path: str | None = None
    error_message: str | None = None
    processed_at: datetime


class ProcessResult(BaseModel):
    """Resumen de una pasada de procesado."""
    total: int = 0
    procesado: int = 0
    sin_regla: int = 0
    error: int = 0
    skipped: int = 0  # ya procesados en pasadas anteriores


class EmailStats(BaseModel):
    total: int = 0
    procesado: int = 0
    sin_regla: int = 0
    error: int = 0
