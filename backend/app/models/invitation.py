"""Modelo SQLAlchemy: Invitation (spec §7.1).

Invitación para dar de alta a un usuario. No hay registro abierto: cada alta
pasa por una invitación con token único de un solo uso y caducidad. El email
queda fijado por la invitación (el invitado no puede cambiarlo al registrarse).
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), index=True)                 # A quién se invita
    token = Column(String(255), unique=True, index=True)    # Token único del enlace
    role = Column(String(20), default="user")               # Rol que tendrá al aceptar
    invited_by = Column(Integer, ForeignKey("users.id"))    # Admin que invita
    status = Column(String(20), default="pending")          # 'pending' | 'accepted' | 'revoked' | 'expired'
    expires_at = Column(DateTime)                           # Caduca (ej: 7 días)
    accepted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    inviter = relationship("User", foreign_keys=[invited_by])
