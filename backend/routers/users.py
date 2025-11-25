from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api_schemas import UserCreate, UserPasswordUpdate, UserUpdate
from backend.auth import require_admin_or_superadmin
from backend.database import Role, User, get_db
from backend.services.user_service import (
    OWNER_ROLE,
    SUPERADMIN_ROLE,
    apply_password,
    ensure_not_last_superadmin,
    generate_unique_email,
    get_user_or_404,
    serialize_user,
)


router = APIRouter(prefix="/api/users", tags=["users"])


def _normalize_avatar(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


@router.get("/")
def list_users(
    db: Session = Depends(get_db),
    _admin_user: User = Depends(require_admin_or_superadmin),
):
    users = db.query(User).join(Role).order_by(User.created_at.desc()).all()
    return [serialize_user(user, include_sensitive=True) for user in users]


@router.get("/{user_id}")
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    _admin_user: User = Depends(require_admin_or_superadmin),
):
    user = get_user_or_404(db, user_id)
    return serialize_user(user, include_sensitive=True)


@router.post("/")
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _admin_user: User = Depends(require_admin_or_superadmin),
):
    requester_role = (_admin_user.role.name if _admin_user.role else "").lower()
    allowed_roles = {OWNER_ROLE, "admin"}
    if requester_role == SUPERADMIN_ROLE:
        allowed_roles.add(SUPERADMIN_ROLE)

    target_role = (payload.role or OWNER_ROLE).lower()
    if target_role not in allowed_roles:
        raise HTTPException(status_code=400, detail="No tienes permisos para crear ese rol")

    role = db.query(Role).filter(Role.name == target_role).first()
    if not role:
        raise HTTPException(status_code=400, detail="Rol no disponible")

    existing_site_owner = None

    def _has_username_conflict() -> bool:
        query = db.query(User).filter(User.username == payload.username)
        if existing_site_owner:
            query = query.filter(User.id != existing_site_owner.id)
        return query.first() is not None

    def _has_email_conflict(email_value: Optional[str]) -> bool:
        if not email_value:
            return False
        query = db.query(User).filter(User.email == email_value)
        if existing_site_owner:
            query = query.filter(User.id != existing_site_owner.id)
        return query.first() is not None

    site_id = payload.site_id if target_role == OWNER_ROLE else None
    if target_role == OWNER_ROLE:
        if not site_id:
            raise HTTPException(status_code=400, detail="Debes asignar un sitio al owner")
        existing_site_owner = db.query(User).filter(User.site_id == site_id).first()

    normalized_email = (payload.email or "").strip() or None

    if _has_username_conflict():
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
    if _has_email_conflict(normalized_email):
        raise HTTPException(status_code=400, detail="El correo ya existe")

    resolved_email = normalized_email or generate_unique_email(db, payload.username)

    avatar_url = _normalize_avatar(payload.avatar_url)

    if existing_site_owner:
        user = existing_site_owner
        user.username = payload.username
        user.email = resolved_email
        user.role_id = role.id
        user.is_active = payload.is_active
        user.avatar_url = avatar_url
        if payload.is_active and not user.activated_at:
            user.activated_at = datetime.utcnow()
        user.expires_at = payload.expires_at
        apply_password(user, payload.password)
    else:
        user = User(
            username=payload.username,
            email=resolved_email,
            role_id=role.id,
            site_id=site_id,
            is_active=payload.is_active,
            activated_at=datetime.utcnow() if payload.is_active else None,
            expires_at=payload.expires_at,
            avatar_url=avatar_url,
        )
        apply_password(user, payload.password)
        db.add(user)

    db.commit()
    db.refresh(user)
    return serialize_user(user, include_sensitive=True)


@router.put("/{user_id}")
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _admin_user: User = Depends(require_admin_or_superadmin),
):
    user = get_user_or_404(db, user_id)
    fields_set = getattr(payload, "model_fields_set", set())
    was_active = user.is_active

    if payload.username and payload.username != user.username:
        if db.query(User).filter(User.username == payload.username).first():
            raise HTTPException(status_code=400, detail="Nombre de usuario en uso")
        user.username = payload.username

    if "email" in fields_set:
        normalized_email = (payload.email or "").strip() or None
        if normalized_email != user.email:
            if normalized_email and db.query(User).filter(User.email == normalized_email).first():
                raise HTTPException(status_code=400, detail="Correo en uso")
            user.email = normalized_email

    if payload.is_active is not None:
        if not payload.is_active:
            ensure_not_last_superadmin(db, user)
        user.is_active = payload.is_active
        if payload.is_active and not was_active:
            user.activated_at = datetime.utcnow()

    if payload.site_id is not None and user.role and user.role.name == OWNER_ROLE:
        if payload.site_id != user.site_id:
            raise HTTPException(status_code=400, detail="No se permite reasignar el sitio de un owner")

    if "expires_at" in fields_set:
        user.expires_at = payload.expires_at

    if payload.password:
        apply_password(user, payload.password)

    if "avatar_url" in fields_set:
        user.avatar_url = _normalize_avatar(payload.avatar_url)

    db.commit()
    db.refresh(user)
    return serialize_user(user, include_sensitive=True)


@router.post("/{user_id}/password")
def update_user_password(
    user_id: int,
    payload: UserPasswordUpdate,
    db: Session = Depends(get_db),
    _admin_user: User = Depends(require_admin_or_superadmin),
):
    user = get_user_or_404(db, user_id)
    apply_password(user, payload.password)
    db.commit()
    return {
        "message": "Contraseña actualizada",
        "user": serialize_user(user, include_sensitive=True),
    }


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _admin_user: User = Depends(require_admin_or_superadmin),
):
    user = get_user_or_404(db, user_id)
    ensure_not_last_superadmin(db, user)
    db.delete(user)
    db.commit()
    return {"message": "Usuario eliminado"}