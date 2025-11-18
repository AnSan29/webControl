from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api_schemas import UserCreate, UserPasswordUpdate, UserUpdate
from backend.auth import require_superadmin
from backend.database import Role, User, get_db
from backend.services.user_service import (
    OWNER_ROLE,
    apply_password,
    ensure_not_last_superadmin,
    get_user_or_404,
    serialize_user,
)


router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/")
def list_users(
    db: Session = Depends(get_db),
    _superadmin: User = Depends(require_superadmin),
):
    users = db.query(User).join(Role).order_by(User.created_at.desc()).all()
    return [serialize_user(user, include_sensitive=True) for user in users]


@router.get("/{user_id}")
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    _superadmin: User = Depends(require_superadmin),
):
    user = get_user_or_404(db, user_id)
    return serialize_user(user, include_sensitive=True)


@router.post("/")
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _superadmin: User = Depends(require_superadmin),
):
    target_role = (payload.role or OWNER_ROLE).lower()
    if target_role not in {OWNER_ROLE, "admin"}:
        raise HTTPException(status_code=400, detail="Solo se permiten roles owner o admin")

    role = db.query(Role).filter(Role.name == target_role).first()
    if not role:
        raise HTTPException(status_code=400, detail="Rol no disponible")

    existing_site_owner = None

    def _has_username_conflict() -> bool:
        query = db.query(User).filter(User.username == payload.username)
        if existing_site_owner:
            query = query.filter(User.id != existing_site_owner.id)
        return query.first() is not None

    def _has_email_conflict() -> bool:
        query = db.query(User).filter(User.email == payload.email)
        if existing_site_owner:
            query = query.filter(User.id != existing_site_owner.id)
        return query.first() is not None

    site_id = payload.site_id if target_role == OWNER_ROLE else None
    if target_role == OWNER_ROLE:
        if not site_id:
            raise HTTPException(status_code=400, detail="Debes asignar un sitio al owner")
        existing_site_owner = db.query(User).filter(User.site_id == site_id).first()

    if _has_username_conflict():
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
    if _has_email_conflict():
        raise HTTPException(status_code=400, detail="El correo ya existe")

    if existing_site_owner:
        user = existing_site_owner
        user.username = payload.username
        user.email = payload.email
        user.role_id = role.id
        user.is_active = payload.is_active
        if payload.is_active and not user.activated_at:
            user.activated_at = datetime.utcnow()
        user.expires_at = payload.expires_at
        apply_password(user, payload.password)
    else:
        user = User(
            username=payload.username,
            email=payload.email,
            role_id=role.id,
            site_id=site_id,
            is_active=payload.is_active,
            activated_at=datetime.utcnow() if payload.is_active else None,
            expires_at=payload.expires_at,
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
    _superadmin: User = Depends(require_superadmin),
):
    user = get_user_or_404(db, user_id)
    fields_set = getattr(payload, "model_fields_set", set())
    was_active = user.is_active

    if payload.username and payload.username != user.username:
        if db.query(User).filter(User.username == payload.username).first():
            raise HTTPException(status_code=400, detail="Nombre de usuario en uso")
        user.username = payload.username

    if payload.email and payload.email != user.email:
        if db.query(User).filter(User.email == payload.email).first():
            raise HTTPException(status_code=400, detail="Correo en uso")
        user.email = payload.email

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

    db.commit()
    db.refresh(user)
    return serialize_user(user, include_sensitive=True)


@router.post("/{user_id}/password")
def update_user_password(
    user_id: int,
    payload: UserPasswordUpdate,
    db: Session = Depends(get_db),
    _superadmin: User = Depends(require_superadmin),
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
    _superadmin: User = Depends(require_superadmin),
):
    user = get_user_or_404(db, user_id)
    ensure_not_last_superadmin(db, user)
    db.delete(user)
    db.commit()
    return {"message": "Usuario eliminado"}