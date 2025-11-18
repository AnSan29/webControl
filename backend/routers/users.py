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
    return [serialize_user(user) for user in users]


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

    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="El correo ya existe")

    site_id = payload.site_id if target_role == OWNER_ROLE else None
    if target_role == OWNER_ROLE:
        if not site_id:
            raise HTTPException(status_code=400, detail="Debes asignar un sitio al owner")
        exists_owner = db.query(User).filter(User.site_id == site_id).first()
        if exists_owner:
            raise HTTPException(status_code=400, detail="El sitio ya cuenta con un dueño")

    user = User(
        username=payload.username,
        email=payload.email,
        role_id=role.id,
        site_id=site_id,
        is_active=payload.is_active,
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

    if payload.site_id is not None and user.role and user.role.name == OWNER_ROLE:
        if payload.site_id != user.site_id:
            raise HTTPException(status_code=400, detail="No se permite reasignar el sitio de un owner")

    db.commit()
    db.refresh(user)
    return serialize_user(user)


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