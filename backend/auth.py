from __future__ import annotations

import os
import secrets
import string
from datetime import datetime, timedelta
from typing import Callable, Iterable, List, Optional

import bcrypt  # type: ignore
from fastapi import Depends, HTTPException, status  # type: ignore
from fastapi.security import OAuth2PasswordBearer  # type: ignore
from jose import JWTError, jwt  # type: ignore
from sqlalchemy import or_  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from database import Admin, Role, User, get_db
from permissions import get_permissions_for_role, is_admin

SECRET_KEY = os.getenv("SECRET_KEY", "cambiar-por-clave-secreta-segura")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))

admin_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


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


def _create_token(data: dict, expires_delta: Optional[timedelta], token_type: str, default_minutes: int) -> str:
    to_encode = data.copy()
    to_encode.setdefault("sub", data.get("sub"))
    to_encode["token_type"] = token_type
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=default_minutes))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crear token de acceso (compatibilidad con endpoints existentes)."""
    data = data.copy()
    data.setdefault("token_type", "access")
    return _create_token(data, expires_delta, "access", ACCESS_TOKEN_EXPIRE_MINUTES)


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crear token de refresco."""
    data = data.copy()
    data["token_type"] = "refresh"
    return _create_token(data, expires_delta, "refresh", REFRESH_TOKEN_EXPIRE_MINUTES)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:  # pragma: no cover - FastAPI maneja excepciones
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def authenticate_admin(db: Session, email: str, password: str):
    """Autenticar administrador heredado."""
    admin = db.query(Admin).filter(Admin.email == email).first()
    if not admin or not verify_password(password, admin.hashed_password):
        return None
    return admin


def authenticate_user(db: Session, username_or_email: str, password: str) -> Optional[User]:
    """Autenticar usuario por username o email."""
    user = (
        db.query(User)
        .filter(or_(User.username == username_or_email, User.email == username_or_email))
        .first()
    )
    if not user or not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario deshabilitado")
    return user


def build_user_claims(user: User) -> dict:
    return {
        "sub": str(user.id),
        "role": user.role.name if user.role else None,
        "permissions": get_permissions_for_role(user.role.name if user.role else None),
    }


def create_token_pair_for_user(user: User) -> tuple[str, str]:
    claims = build_user_claims(user)
    access_token = create_access_token(claims)
    refresh_token = create_refresh_token(claims)
    return access_token, refresh_token


async def get_current_admin(
    token: str = Depends(admin_oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Obtener admin actual desde token legado."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    subject = payload.get("sub")
    if subject is None:
        raise credentials_exception

    admin_user = None
    if str(subject).isdigit():
        admin_user = db.query(User).filter(User.id == int(subject)).first()
    else:
        admin = db.query(Admin).filter(Admin.email == subject).first()
        if admin is None:
            raise credentials_exception
        admin_user = db.query(User).filter(User.email == admin.email).first()
        if admin_user is None:
            return admin  # Compatibilidad temporal

    if not admin_user or not admin_user.role or admin_user.role.name != "admin":
        raise credentials_exception
    return admin_user


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_token(token)
    if payload.get("token_type") != "access":
        raise HTTPException(status_code=401, detail="Token de acceso requerido")
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario deshabilitado")
    return user


def require_roles(*roles: str) -> Callable:
    async def dependency(current_user: User = Depends(get_current_user)) -> User:
        if not roles:
            return current_user
        user_role = current_user.role.name if current_user.role else None
        if user_role not in roles:
            raise HTTPException(status_code=403, detail="Permisos insuficientes")
        return current_user

    return dependency


def get_user_permissions(user: User) -> List[str]:
    return get_permissions_for_role(user.role.name if user.role else None)


def user_is_admin(user: User) -> bool:
    return is_admin(user)
