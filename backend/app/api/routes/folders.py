"""Router de carpetas de Dropbox (spec §8.6).

CRUD de las carpetas destino + navegador de las carpetas reales en Dropbox.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.middleware import get_current_user
from app.database import get_db
from app.models.folder import Folder
from app.models.user import User
from app.schemas.folder import DropboxEntry, FolderCreate, FolderOut, FolderUpdate
from app.services import dropbox_service
from app.utils.security import encryptor

router = APIRouter(prefix="/folders", tags=["folders"])


@router.get("", response_model=list[FolderOut])
def list_folders(db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    return (
        db.query(Folder)
        .filter(Folder.user_id == current.id)
        .order_by(Folder.created_at)
        .all()
    )


@router.post("", response_model=FolderOut, status_code=status.HTTP_201_CREATED)
def create_folder(
    data: FolderCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    # Crea la carpeta en Dropbox (si hay token y la ruta no es la raíz).
    path = data.dropbox_path.strip()
    if current.dropbox_access_token and path not in ("", "/"):
        try:
            dropbox_service.create_folder(
                encryptor.decrypt(current.dropbox_access_token), path
            )
        except RuntimeError as exc:
            raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Dropbox: {exc}")

    folder = Folder(
        user_id=current.id,
        name=data.name,
        dropbox_path=path,
        doc_type=data.doc_type,
        organize_by_date=data.organize_by_date,
    )
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return folder


def _get_own_folder(db: Session, folder_id: int, user: User) -> Folder:
    folder = (
        db.query(Folder)
        .filter(Folder.id == folder_id, Folder.user_id == user.id)
        .first()
    )
    if not folder:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Carpeta no encontrada")
    return folder


@router.put("/{folder_id}", response_model=FolderOut)
def update_folder(
    folder_id: int,
    data: FolderUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    folder = _get_own_folder(db, folder_id, current)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(folder, field, value)
    db.commit()
    db.refresh(folder)
    return folder


@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_folder(
    folder_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)
):
    db.delete(_get_own_folder(db, folder_id, current))
    db.commit()


@router.get("/dropbox/browse", response_model=list[DropboxEntry])
def browse_dropbox(
    path: str = "", current: User = Depends(get_current_user)
):
    """Navega carpetas reales de Dropbox ("" = raíz)."""
    if not current.dropbox_access_token:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Configura primero tu token de Dropbox en el perfil.",
        )
    try:
        return dropbox_service.list_folders(
            encryptor.decrypt(current.dropbox_access_token), path
        )
    except RuntimeError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc))
