"""Conexiones a MariaDB (SQLAlchemy) y MongoDB (PyMongo)."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# --- MariaDB / SQLAlchemy ---
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependencia de FastAPI: abre una sesión por request y la cierra al final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- MongoDB / PyMongo ---
# El usuario root de Mongo vive en la base "admin", por eso authSource=admin.
from pymongo import MongoClient  # noqa: E402  (import agrupado con su bloque)

mongo_client = MongoClient(settings.MONGODB_URL, authSource="admin")
mongo_db = mongo_client.get_default_database()


# --- Bootstrap de esquema (idempotente) ---
def init_db() -> None:
    """Crea las tablas de MariaDB que aún no existan (spec §7.1).

    Importa el paquete de modelos para registrarlos en el metadata de Base antes
    de crear las tablas.
    """
    from app import models  # noqa: F401  (registra todos los modelos)

    Base.metadata.create_all(bind=engine)


def init_mongo() -> None:
    """Crea las colecciones de MongoDB que aún no existan (spec §7.2)."""
    existing = set(mongo_db.list_collection_names())

    if "email_attachments" not in existing:
        mongo_db.create_collection(
            "email_attachments",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "properties": {
                        "user_id": {"bsonType": "int"},
                        "gmail_message_id": {"bsonType": "string"},
                        "attachments": {
                            "bsonType": "array",
                            "items": {
                                "bsonType": "object",
                                "properties": {
                                    "filename": {"bsonType": "string"},
                                    "mime_type": {"bsonType": "string"},
                                    "size": {"bsonType": "int"},
                                    "dropbox_path": {"bsonType": "string"},
                                },
                            },
                        },
                        "created_at": {"bsonType": "date"},
                    },
                }
            },
        )

    if "user_preferences" not in existing:
        mongo_db.create_collection("user_preferences")
