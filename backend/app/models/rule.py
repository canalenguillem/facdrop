"""Modelo SQLAlchemy: Rule (spec §7.1).

Regla: condición (etiqueta vigilada + remitente/asunto) → carpeta de Dropbox.
Se evalúan por `priority` (menor = antes); la primera que coincide gana.
"""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(255), index=True)
    doc_type = Column(String(50))         # 'factura' | 'albaran'

    # Condiciones (qué correos coinciden)
    source_label_id = Column(Integer, ForeignKey("gmail_labels.id"))  # En qué etiqueta busca
    from_email = Column(String(255), nullable=True)        # Remitente (ej: proveedor@x.com)
    subject_contains = Column(String(255), nullable=True)  # Texto que debe contener el asunto
    has_attachment = Column(Boolean, default=True)         # Requiere adjunto

    # Destino: carpeta de Dropbox
    dropbox_folder_id = Column(Integer, ForeignKey("folders.id"))

    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # Orden de evaluación (menor = antes)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="rules")
    source_label = relationship("GmailLabel")
    dropbox_folder = relationship("Folder")
