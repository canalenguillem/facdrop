"""Modelo SQLAlchemy: CredentialLog (spec §7.1).

Auditoría de credenciales: cada alta, cambio, prueba o borrado de una credencial
de servicio (Gmail / Dropbox) queda registrado aquí.
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class CredentialLog(Base):
    __tablename__ = "credential_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    service = Column(String(50))          # 'gmail' | 'dropbox'
    action = Column(String(50))           # 'added' | 'updated' | 'removed' | 'tested'
    test_result = Column(String(50), nullable=True)  # 'success' | 'failed'
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="credential_logs")
