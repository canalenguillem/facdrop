"""Schemas Pydantic de reglas (spec §8.5)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RuleCreate(BaseModel):
    name: str
    doc_type: str                       # 'factura' | 'albaran'
    source_label_id: int                # etiqueta vigilada (gmail_labels.id)
    dropbox_folder_id: int              # carpeta destino (folders.id)
    from_email: str | None = None
    subject_contains: str | None = None
    has_attachment: bool = True
    is_active: bool = True
    priority: int = 0


class RuleUpdate(BaseModel):
    name: str | None = None
    doc_type: str | None = None
    source_label_id: int | None = None
    dropbox_folder_id: int | None = None
    from_email: str | None = None
    subject_contains: str | None = None
    has_attachment: bool | None = None
    is_active: bool | None = None
    priority: int | None = None


class RuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    doc_type: str
    source_label_id: int
    dropbox_folder_id: int
    from_email: str | None
    subject_contains: str | None
    has_attachment: bool
    is_active: bool
    priority: int
    created_at: datetime


class RuleReorderItem(BaseModel):
    id: int
    priority: int


class RuleReorder(BaseModel):
    items: list[RuleReorderItem]


class RuleTestEmail(BaseModel):
    """Correo de ejemplo para probar reglas (spec §8.5 /rules/{id}/test)."""
    label_id: str
    from_email: str = ""
    subject: str = ""
    has_attachments: bool = True


class RuleTestResult(BaseModel):
    matched: bool
    rule_id: int | None = None
    rule_name: str | None = None