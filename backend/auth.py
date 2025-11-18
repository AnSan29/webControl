import os
import secrets
import string
from datetime import datetime, timedelta
from typing import Callable, Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.database import get_db, Role, User

SUPERADMIN_ROLE = "superadmin"
ADMIN_ROLE = "admin"
OWNER_ROLE = "owner"

SECRET_KEY = os.getenv("SECRET_KEY", "cambiar-por-clave-secreta-segura")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


def hash_password(password: str) -> str:
	"""Hash de contraseña con bcrypt"""
	password_bytes = password.encode("utf-8")[:72]
	salt = bcrypt.gensalt()
	return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
	"""Verificar contraseña"""
	plain_password_bytes = plain_password.encode("utf-8")[:72]
	hashed_password_bytes = hashed_password.encode("utf-8")
	return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)


def get_password_hash(password: str) -> str:
    """Alias para compatibilidad"""
    return hash_password(password)


def generate_temporary_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()"
    return "".join(secrets.choice(alphabet) for _ in range(length))



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crear token JWT con la expiración configurada."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



def authenticate_user(db: Session, identifier: str, password: str) -> Optional[User]:
    """Autenticar por username o email."""
    user = (
        db.query(User)
        .join(Role)
        .filter(
            or_(
                User.email == identifier,
                User.username == identifier,
            )
        )
        .first()
    )
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def build_user_claims(user: User) -> dict:
    return {
        "sub": str(user.id),
        "role": user.role.name if user.role else None,
        "username": user.username,
    }


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Obtener usuario autenticado desde el token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def _has_role(user: User, *roles: str) -> bool:
    """Helper para validar si el usuario tiene alguno de los roles permitidos."""
    if not user.role:
        return False
    normalized = (user.role.name or "").lower()
    return normalized in {role.lower() for role in roles}


def require_superadmin(current_user: User = Depends(get_current_user)) -> User:
    """Asegura que el usuario tenga rol superadmin."""
    if not _has_role(current_user, SUPERADMIN_ROLE):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso restringido al superadmin")
    return current_user


def require_roles(*roles: str) -> Callable[[User], User]:
    """Crea un guard dinámico que permite solo los roles especificados."""

    allowed = {role.lower() for role in roles if role}
    if not allowed:
        raise ValueError("Debes especificar al menos un rol permitido")

    def _dependency(current_user: User = Depends(get_current_user)) -> User:
        if not _has_role(current_user, *allowed):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para esta acción")
        return current_user

    return _dependency


def require_owner_of_site(
    site_id: int,
    current_user: User = Depends(get_current_user),
) -> User:
    """Permite acceso a superadmins, administradores o owners del sitio indicado."""

    if _has_role(current_user, SUPERADMIN_ROLE, ADMIN_ROLE):
        return current_user

    if _has_role(current_user, OWNER_ROLE) and current_user.site_id == site_id:
        return current_user

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes acceder a este sitio")
