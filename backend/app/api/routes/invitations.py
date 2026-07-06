"""Router de invitaciones (spec §8.2) — solo admin."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.middleware import require_admin
from app.database import get_db
from app.models.invitation import Invitation
from app.models.user import User
from app.schemas.invitation import InvitationCreate, InvitationOut
from app.services import email_service, invitation_service

router = APIRouter(prefix="/invitations", tags=["invitations"])


def _with_link(inv: Invitation) -> Invitation:
    """Adjunta el enlace de invitación al objeto (solo para las pendientes)."""
    if inv.status == "pending":
        inv.invite_link = invitation_service.build_invite_link(inv.token)
    return inv


@router.get("", response_model=list[InvitationOut])
def list_invitations(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    invs = db.query(Invitation).order_by(Invitation.created_at.desc()).all()
    return [_with_link(i) for i in invs]


@router.post("", response_model=InvitationOut, status_code=status.HTTP_201_CREATED)
def create_invitation(
    data: InvitationCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    if invitation_service.email_already_registered(db, data.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ese email ya tiene cuenta")

    inv = invitation_service.create_invitation(db, data.email, data.role, admin.id)
    link = invitation_service.build_invite_link(inv.token)
    inv.email_sent = email_service.send_invitation_email(inv.email, link)
    inv.invite_link = link
    return inv


@router.delete("/{inv_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_invitation(
    inv_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)
):
    inv = db.query(Invitation).filter(Invitation.id == inv_id).first()
    if not inv:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invitación no encontrada")
    if inv.status != "pending":
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Solo se pueden revocar invitaciones pendientes",
        )
    inv.status = "revoked"
    db.commit()


@router.post("/{inv_id}/resend", response_model=InvitationOut)
def resend_invitation(
    inv_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)
):
    inv = db.query(Invitation).filter(Invitation.id == inv_id).first()
    if not inv:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invitación no encontrada")
    if inv.status != "pending":
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Solo se pueden reenviar invitaciones pendientes",
        )
    link = invitation_service.build_invite_link(inv.token)
    inv.email_sent = email_service.send_invitation_email(inv.email, link)
    inv.invite_link = link
    return inv
