"""Router de usuarios y perfil (spec §8.3).

En esta fase: datos del usuario actual (/me) y gestión de usuarios por admin.
Los endpoints de credenciales Gmail/Dropbox (/me/credentials/*) llegan en la
Fase 4 (encriptación).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.middleware import get_current_user, require_admin
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserAdminUpdate, UserOut, UserUpdateMe

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_me(current: User = Depends(get_current_user)):
    return current


@router.put("/me", response_model=UserOut)
def update_me(
    data: UserUpdateMe,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if data.username is not None:
        clash = (
            db.query(User)
            .filter(User.username == data.username, User.id != current.id)
            .first()
        )
        if clash:
            raise HTTPException(status.HTTP_409_CONFLICT, "Ese username ya está en uso")
        current.username = data.username
    db.commit()
    db.refresh(current)
    return current


@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(User).order_by(User.created_at).all()


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    data: UserAdminUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.role is not None:
        user.role = data.role
        user.is_admin = data.role == "admin"
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    if user_id == admin.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No puedes eliminarte a ti mismo")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    db.delete(user)
    db.commit()
