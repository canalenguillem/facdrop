"""Router de reglas (spec §8.5).

Una regla conecta: etiqueta vigilada + (remitente/asunto) → carpeta de Dropbox.
Se evalúan por prioridad (menor = antes) con el RuleEngine (spec §11).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.middleware import get_current_user
from app.database import get_db
from app.models.folder import Folder
from app.models.gmail_label import GmailLabel
from app.models.rule import Rule
from app.models.user import User
from app.schemas.rule import (
    RuleCreate,
    RuleOut,
    RuleReorder,
    RuleTestEmail,
    RuleTestResult,
    RuleUpdate,
)
from app.services.rule_engine import RuleEngine

router = APIRouter(prefix="/rules", tags=["rules"])


def _validate_refs(db: Session, user: User, label_id: int, folder_id: int) -> None:
    """La etiqueta y la carpeta referenciadas deben ser del propio usuario."""
    label = (
        db.query(GmailLabel)
        .filter(GmailLabel.id == label_id, GmailLabel.user_id == user.id)
        .first()
    )
    if not label:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "source_label_id no válido")
    folder = (
        db.query(Folder)
        .filter(Folder.id == folder_id, Folder.user_id == user.id)
        .first()
    )
    if not folder:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "dropbox_folder_id no válido")


def _get_own_rule(db: Session, rule_id: int, user: User) -> Rule:
    rule = db.query(Rule).filter(Rule.id == rule_id, Rule.user_id == user.id).first()
    if not rule:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Regla no encontrada")
    return rule


@router.get("", response_model=list[RuleOut])
def list_rules(db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    return (
        db.query(Rule)
        .filter(Rule.user_id == current.id)
        .order_by(Rule.priority, Rule.id)
        .all()
    )


@router.post("", response_model=RuleOut, status_code=status.HTTP_201_CREATED)
def create_rule(
    data: RuleCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    _validate_refs(db, current, data.source_label_id, data.dropbox_folder_id)
    rule = Rule(user_id=current.id, **data.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.get("/{rule_id}", response_model=RuleOut)
def get_rule(
    rule_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)
):
    return _get_own_rule(db, rule_id, current)


@router.put("/{rule_id}", response_model=RuleOut)
def update_rule(
    rule_id: int,
    data: RuleUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    rule = _get_own_rule(db, rule_id, current)
    changes = data.model_dump(exclude_unset=True)
    # Si se cambian las referencias, revalidar propiedad.
    new_label = changes.get("source_label_id", rule.source_label_id)
    new_folder = changes.get("dropbox_folder_id", rule.dropbox_folder_id)
    if "source_label_id" in changes or "dropbox_folder_id" in changes:
        _validate_refs(db, current, new_label, new_folder)
    for field, value in changes.items():
        setattr(rule, field, value)
    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(
    rule_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)
):
    db.delete(_get_own_rule(db, rule_id, current))
    db.commit()


@router.post("/reorder", response_model=list[RuleOut])
def reorder_rules(
    data: RuleReorder,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Actualiza la prioridad de varias reglas del usuario a la vez."""
    own = {r.id: r for r in db.query(Rule).filter(Rule.user_id == current.id).all()}
    for item in data.items:
        rule = own.get(item.id)
        if not rule:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Regla {item.id} no encontrada")
        rule.priority = item.priority
    db.commit()
    return (
        db.query(Rule)
        .filter(Rule.user_id == current.id)
        .order_by(Rule.priority, Rule.id)
        .all()
    )


@router.post("/{rule_id}/test", response_model=RuleTestResult)
def test_rule(
    rule_id: int,
    email: RuleTestEmail,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Prueba una regla concreta contra un correo de ejemplo (spec §8.5)."""
    rule = _get_own_rule(db, rule_id, current)
    email_dict = {
        "label_id": email.label_id,
        "from": email.from_email,
        "subject": email.subject,
        "has_attachments": email.has_attachments,
    }
    matched = RuleEngine()._matches(email_dict, rule)
    return RuleTestResult(
        matched=matched,
        rule_id=rule.id if matched else None,
        rule_name=rule.name if matched else None,
    )
