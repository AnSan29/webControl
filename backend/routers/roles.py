from typing import List

from fastapi import APIRouter, Depends, HTTPException, status  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from auth import get_current_user, require_roles
from database import Role, User, get_db
from schemas import RoleCreate, RoleRead, RoleUpdate

router = APIRouter(prefix="/roles", tags=["Roles"])
admin_required = require_roles("admin")


def _ensure_role_exists(db: Session, role_id: int) -> Role:
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return role


@router.get("/", response_model=List[RoleRead])
def list_roles(
    db: Session = Depends(get_db),
    _: Role = Depends(admin_required),
):
    return db.query(Role).order_by(Role.name.asc()).all()


@router.get("/{role_id}", response_model=RoleRead)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    _: Role = Depends(admin_required),
):
    return _ensure_role_exists(db, role_id)


@router.post("/", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
def create_role(
    payload: RoleCreate,
    db: Session = Depends(get_db),
    _: Role = Depends(admin_required),
):
    existing = db.query(Role).filter(Role.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="El rol ya existe")

    role = Role(name=payload.name, description=payload.description)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.patch("/{role_id}", response_model=RoleRead)
def update_role(
    role_id: int,
    payload: RoleUpdate,
    db: Session = Depends(get_db),
    _: Role = Depends(admin_required),
):
    role = _ensure_role_exists(db, role_id)

    if payload.name and payload.name != role.name:
        conflict = db.query(Role).filter(Role.name == payload.name).first()
        if conflict and conflict.id != role.id:
            raise HTTPException(status_code=400, detail="Ya existe un rol con ese nombre")
        role.name = payload.name

    if payload.description is not None:
        role.description = payload.description

    db.commit()
    db.refresh(role)
    return role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    _: Role = Depends(admin_required),
):
    role = _ensure_role_exists(db, role_id)

    linked_users = db.query(User).filter(User.role_id == role.id).count()
    if linked_users:
        raise HTTPException(status_code=400, detail="No se puede eliminar un rol con usuarios asociados")

    db.delete(role)
    db.commit()
    return None
