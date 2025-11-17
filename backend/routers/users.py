from typing import List

from fastapi import APIRouter, Depends, HTTPException, status  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from auth import get_current_user, hash_password, require_roles
from database import Role, Site, SiteAssignment, User, get_db
from permissions import can_manage_users
from schemas import (
    SiteAssignmentCreate,
    SiteAssignmentRead,
    UserCreate,
    UserPasswordUpdate,
    UserRead,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["Usuarios"])
admin_required = require_roles("admin")


def _serialize_user(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        username=user.username,
        email=user.email,
        role_id=user.role_id,
        role_name=user.role.name if user.role else None,
        site_id=user.site_id,
        is_active=user.is_active,
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def _ensure_user(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


def _require_admin_or_self(current_user: User, target_user: User):
    if current_user.id == target_user.id:
        return
    if not can_manage_users(current_user):
        raise HTTPException(status_code=403, detail="No tienes permisos para esta acción")


@router.get("/", response_model=List[UserRead])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(admin_required),
):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [_serialize_user(user) for user in users]


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(admin_required),
):
    return _serialize_user(_ensure_user(db, user_id))


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(admin_required),
):
    username_exists = db.query(User).filter(User.username == payload.username).first()
    email_exists = db.query(User).filter(User.email == payload.email).first()
    if username_exists or email_exists:
        raise HTTPException(status_code=400, detail="Usuario o email ya registrado")

    # Resolver role_id desde role (string) si es necesario
    role_id = payload.role_id
    if payload.role:
        role = db.query(Role).filter(Role.name == payload.role).first()
        if not role:
            raise HTTPException(status_code=400, detail="Rol inválido")
        role_id = role.id
    elif role_id:
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=400, detail="Rol inválido")
    else:
        raise HTTPException(status_code=400, detail="role o role_id requerido")

    if payload.site_id:
        site = db.query(Site).filter(Site.id == payload.site_id).first()
        if not site:
            raise HTTPException(status_code=400, detail="El sitio no existe")

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role_id=role_id,
        site_id=payload.site_id,
        is_active=payload.is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _serialize_user(user)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target = _ensure_user(db, user_id)
    _require_admin_or_self(current_user, target)

    if payload.username and payload.username != target.username:
        conflict = db.query(User).filter(User.username == payload.username).first()
        if conflict and conflict.id != target.id:
            raise HTTPException(status_code=400, detail="Nombre de usuario ya en uso")
        target.username = payload.username

    if payload.email and payload.email != target.email:
        conflict = db.query(User).filter(User.email == payload.email).first()
        if conflict and conflict.id != target.id:
            raise HTTPException(status_code=400, detail="Email ya registrado")
        target.email = payload.email

    # Manejar actualización de rol
    if payload.role or payload.role_id:
        if not can_manage_users(current_user):
            raise HTTPException(status_code=403, detail="Solo un admin puede cambiar roles")
        
        role_id = payload.role_id
        if payload.role:
            role = db.query(Role).filter(Role.name == payload.role).first()
            if not role:
                raise HTTPException(status_code=400, detail="Rol inválido")
            role_id = role.id
        
        if role_id:
            role = db.query(Role).filter(Role.id == role_id).first()
            if not role:
                raise HTTPException(status_code=400, detail="Rol inválido")
            target.role_id = role_id

    if payload.site_id is not None:
        if not can_manage_users(current_user):
            raise HTTPException(status_code=403, detail="Solo un admin puede reasignar sitios")
        if payload.site_id:
            site = db.query(Site).filter(Site.id == payload.site_id).first()
            if not site:
                raise HTTPException(status_code=400, detail="El sitio no existe")
        target.site_id = payload.site_id

    if payload.is_active is not None:
        if not can_manage_users(current_user):
            raise HTTPException(status_code=403, detail="Solo un admin puede activar/desactivar usuarios")
        target.is_active = payload.is_active

    db.commit()
    db.refresh(target)
    return _serialize_user(target)


@router.patch("/{user_id}/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    user_id: int,
    payload: UserPasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target = _ensure_user(db, user_id)
    _require_admin_or_self(current_user, target)

    target.hashed_password = hash_password(payload.password)
    db.commit()
    return None


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(admin_required),
):
    user = _ensure_user(db, user_id)
    db.delete(user)
    db.commit()
    return None


@router.post("/{user_id}/assignments", response_model=SiteAssignmentRead, status_code=status.HTTP_201_CREATED)
def assign_site(
    user_id: int,
    payload: SiteAssignmentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(admin_required),
):
    user = _ensure_user(db, user_id)
    site = db.query(Site).filter(Site.id == payload.site_id).first()
    if not site:
        raise HTTPException(status_code=400, detail="El sitio no existe")

    existing = (
        db.query(SiteAssignment)
        .filter(
            SiteAssignment.site_id == payload.site_id,
            SiteAssignment.user_id == user.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="El usuario ya está asignado a este sitio")

    assignment = SiteAssignment(
        site_id=payload.site_id,
        user_id=user.id,
        permission=payload.permission,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return SiteAssignmentRead(
        id=assignment.id,
        site_id=assignment.site_id,
        user_id=assignment.user_id,
        permission=assignment.permission,
        created_at=assignment.created_at,
    )


@router.delete("/{user_id}/assignments/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_assignment(
    user_id: int,
    site_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(admin_required),
):
    assignment = (
        db.query(SiteAssignment)
        .filter(
            SiteAssignment.user_id == user_id,
            SiteAssignment.site_id == site_id,
        )
        .first()
    )
    if not assignment:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")

    db.delete(assignment)
    db.commit()
    return None


@router.get("/assignments", response_model=List[dict])
def list_assignments(
    db: Session = Depends(get_db),
    _: User = Depends(admin_required),
):
    """Lista todas las asignaciones de usuarios a sitios"""
    assignments = db.query(SiteAssignment).order_by(SiteAssignment.created_at.desc()).all()
    result = []
    for assignment in assignments:
        user = db.query(User).filter(User.id == assignment.user_id).first()
        site = db.query(Site).filter(Site.id == assignment.site_id).first()
        result.append({
            "id": assignment.id,
            "user_id": assignment.user_id,
            "user_email": user.email if user else "N/A",
            "site_id": assignment.site_id,
            "site_name": site.name if site else "N/A",
            "role": assignment.permission,
            "assigned_at": assignment.created_at.isoformat() if assignment.created_at else None,
        })
    return result


@router.delete("/assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(admin_required),
):
    """Elimina una asignación de usuario a sitio"""
    assignment = db.query(SiteAssignment).filter(SiteAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    
    db.delete(assignment)
    db.commit()
    return None
