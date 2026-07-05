"""Paquete de modelos SQLAlchemy.

Importa todos los modelos aquí para que queden registrados en el metadata de
`Base` (necesario para que `Base.metadata.create_all()` cree todas las tablas y
para que las relaciones por nombre de clase se resuelvan).
"""
from app.models.user import User
from app.models.invitation import Invitation
from app.models.gmail_label import GmailLabel
from app.models.folder import Folder
from app.models.rule import Rule
from app.models.email_log import EmailLog
from app.models.credential_log import CredentialLog

__all__ = [
    "User",
    "Invitation",
    "GmailLabel",
    "Folder",
    "Rule",
    "EmailLog",
    "CredentialLog",
]
