"""Modelo SQLAlchemy: EmailLog (spec §7.1).

Historial de cada correo procesado. Traza el resultado: 'procesado' (regla
aplicada y adjuntos subidos a Dropbox), 'sin_regla' (ninguna regla coincidió) o
'error'. El correo nunca se toca en Gmail.
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    gmail_message_id = Column(String(255), unique=True, index=True)
    from_email = Column(String(255))
    subject = Column(String(500))
    source_label = Column(String(255))    # Etiqueta de Gmail donde estaba el correo
    doc_type = Column(String(50))         # 'factura' | 'albaran' | 'ignorado'
    rule_applied_id = Column(Integer, ForeignKey("rules.id"), nullable=True)
    status = Column(String(50))           # 'procesado' | 'sin_regla' | 'error'
    error_message = Column(Text, nullable=True)
    dropbox_folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    dropbox_file_path = Column(String(500), nullable=True)  # Ruta final en Dropbox
    processed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="email_logs")
