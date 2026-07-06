"""Modelo SQLAlchemy: User (spec §7.1).

Usuario de la app. Guarda las credenciales de servicio (Gmail App Password,
Dropbox Access Token) ENCRIPTADAS con Fernet — nunca en claro. El frontend solo
ve el estado (`*_connected`), jamás la credencial.
"""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    role = Column(String(20), default="user")  # 'admin' | 'user'

    # Credenciales Gmail (guardadas en el perfil, encriptadas)
    gmail_app_password = Column(String(500), nullable=True)  # Encriptado
    gmail_user_email = Column(String(255), nullable=True)
    gmail_connected = Column(Boolean, default=False)
    gmail_connected_at = Column(DateTime, nullable=True)
    gmail_last_tested = Column(DateTime, nullable=True)
    gmail_test_status = Column(String(50), nullable=True)  # 'success' | 'failed'

    # Credenciales Dropbox (guardadas en el perfil, encriptadas).
    # TEXT (no String(500)): los tokens de Dropbox con scopes, una vez
    # encriptados con Fernet, superan holgadamente los 500 caracteres.
    dropbox_access_token = Column(Text, nullable=True)   # Encriptado (método token pegado)
    # Refresh token OAuth (acceso permanente): no caduca; con él se obtienen
    # access tokens frescos cuando hacen falta. Encriptado.
    dropbox_refresh_token = Column(Text, nullable=True)
    dropbox_connected = Column(Boolean, default=False)
    dropbox_connected_at = Column(DateTime, nullable=True)
    dropbox_last_tested = Column(DateTime, nullable=True)
    dropbox_test_status = Column(String(50), nullable=True)  # 'success' | 'failed'

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones (cada usuario tiene sus etiquetas, reglas, carpetas y logs)
    gmail_labels = relationship("GmailLabel", back_populates="user")
    rules = relationship("Rule", back_populates="user")
    folders = relationship("Folder", back_populates="user")
    email_logs = relationship("EmailLog", back_populates="user")
    credential_logs = relationship("CredentialLog", back_populates="user")
