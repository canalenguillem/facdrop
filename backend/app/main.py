"""
Punto de entrada de la API de Fracdrop.

Al arrancar crea el esquema (tablas + colecciones) y siembra el admin. Registra
los routers implementados hasta ahora. Los routers de las fases siguientes
(labels, rules, folders, emails, integrations) están importados como stubs y se
irán activando conforme se implementen.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, folders, invitations, labels, rules, users
from app.database import SessionLocal, init_db, init_mongo
from app.services.auth_service import seed_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Al arrancar: crea tablas (MariaDB §7.1) y colecciones (MongoDB §7.2) si faltan.
    init_db()
    init_mongo()
    # Admin semilla (spec §9.1)
    db = SessionLocal()
    try:
        seed_admin(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Fracdrop API",
    description="Clasifica adjuntos de Gmail y los envía a carpetas de Dropbox.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS abierto en desarrollo; restringir en producción.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers activos ---
app.include_router(auth.router, prefix="/api")          # Fase 3
app.include_router(users.router, prefix="/api")         # Fase 3 + 4
app.include_router(invitations.router, prefix="/api")   # Fase 3
app.include_router(labels.router, prefix="/api")        # Fase 5
app.include_router(folders.router, prefix="/api")       # Fase 5
app.include_router(rules.router, prefix="/api")         # Fase 5


@app.get("/")
def root():
    return {"service": "fracdrop-backend", "status": "ok", "version": "0.1.0"}


@app.get("/health")
def health():
    """Health check simple (sin tocar BD)."""
    return {"status": "healthy"}
