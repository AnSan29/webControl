from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.auth import require_admin_or_superadmin
from backend.database import Role, get_db
from backend.services.user_service import serialize_role


router = APIRouter(prefix="/api/roles", tags=["roles"])


@router.get("/")
def list_roles(
    db: Session = Depends(get_db),
    _admin_user = Depends(require_admin_or_superadmin),
):
    roles = db.query(Role).order_by(Role.id.asc()).all()
    return [serialize_role(role) for role in roles]


@router.get("/{role_id}")
def get_role_detail(
    role_id: int,
    db: Session = Depends(get_db),
    _admin_user = Depends(require_admin_or_superadmin),
):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return serialize_role(role)