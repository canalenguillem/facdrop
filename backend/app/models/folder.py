"""Modelo SQLAlchemy: Folder (spec §7.1).

Carpeta de Dropbox donde se guardan los adjuntos. El usuario define la ruta
(ej: /Empresa/Facturas/Enero2026) y el tipo de documento que contiene.
"""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(255))            # Nombre amigable (ej: "Facturas Enero 2026")
    dropbox_path = Column(String(500))    # Ruta en Dropbox (ej: /Empresa/Facturas/Enero2026)
    doc_type = Column(String(50))         # 'factura' | 'albaran' | 'otros'
    # Si True, los adjuntos se guardan en subcarpetas por fecha de recepción:
    # {dropbox_path}/AAAA/MM/DD/fichero.pdf
    organize_by_date = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="folders")
