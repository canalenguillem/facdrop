"""Modelo SQLAlchemy: GmailLabel (spec §7.1).

Etiqueta de Gmail que la app vigila (SOLO lectura). La app nunca crea ni mueve
etiquetas: solo lee de las que el usuario marca aquí como vigiladas.
"""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class GmailLabel(Base):
    __tablename__ = "gmail_labels"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    gmail_label_id = Column(String(255), index=True)   # ID real de la etiqueta en Gmail
    gmail_label_name = Column(String(255))             # Ej: "Facturas", "Albaranes"
    is_active = Column(Boolean, default=True)          # Si la app la vigila o no
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="gmail_labels")
