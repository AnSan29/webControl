from __future__ import annotations

import os
import re
import unicodedata
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.database import Role, User
from backend.auth import hash_password

SUPERADMIN_ROLE = "superadmin"
OWNER_ROLE = "owner"

DEFAULT_INTERNAL_EMAIL_DOMAIN = os.getenv(
    "INTERNAL_EMAIL_DOMAIN",
    os.getenv("OWNER_EMAIL_DOMAIN", "owners.webcontrol.local"),
)

ROLE_DISPLAY_NAMES = {
    "superadmin": "Superadmin",
    "admin": "Administrador",
    "owner": "Owner",
}


def slugify_identifier(value: str, fallback: str = "user") -> str:
    value = value or fallback
    normalized = (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower()
    return cleaned or fallback


def generate_unique_username(db: Session, base_value: str) -> str:
    base = slugify_identifier(base_value)
    username = base
    counter = 1
    while db.query(User).filter(User.username == username).first():
        counter += 1
        username = f"{base}-{counter}"
    return username


def generate_unique_email(
    db: Session,
    base_username: str,
    *,
    domain: Optional[str] = None,
) -> str:
    email_domain = domain or DEFAULT_INTERNAL_EMAIL_DOMAIN
    safe_username = slugify_identifier(base_username)
    email = f"{safe_username}@{email_domain}"
    counter = 1
    while db.query(User).filter(User.email == email).first():
        counter += 1
        email = f"{safe_username}-{counter}@{email_domain}"
    return email


def serialize_role(role: Role) -> dict:
    normalized = (role.name or "").strip().lower()
    display_name = ROLE_DISPLAY_NAMES.get(normalized, (role.name or "").title())
    return {
        "id": role.id,
        "name": role.name,
        "display_name": display_name,
        "description": role.description,
        "created_at": role.created_at.isoformat() if role.created_at else None,
        "updated_at": role.updated_at.isoformat() if role.updated_at else None,
    }


def serialize_user(user: User, *, include_sensitive: bool = False) -> dict:
    role_name = user.role.name if user.role else None
    data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar_url": user.avatar_url,
        "role": role_name,
        "role_label": user.role.description if user.role else None,
        "role_display": ROLE_DISPLAY_NAMES.get(role_name, (role_name.title() if role_name else None)),
        "site_id": user.site_id,
        "is_active": user.is_active,
        "activated_at": user.activated_at.isoformat() if user.activated_at else None,
        "expires_at": user.expires_at.isoformat() if user.expires_at else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }
    if user.site:
        data["site"] = {"id": user.site.id, "name": user.site.name}
        data["site_name"] = user.site.name
    else:
        data["site"] = None
        data["site_name"] = None

    if include_sensitive:
        data["plain_password"] = user.plain_password
    return data


def get_user_or_404(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


def ensure_not_last_superadmin(db: Session, user: User) -> None:
    if not user.role or user.role.name != SUPERADMIN_ROLE:
        return
    remaining = (
        db.query(User)
        .join(Role)
        .filter(
            Role.name == SUPERADMIN_ROLE,
            User.id != user.id,
            User.is_active == True,  # noqa: E712
        )
        .count()
    )
    if remaining == 0:
        raise HTTPException(status_code=400, detail="Debe existir al menos un superadmin activo")


def apply_password(user: User, password: str, *, store_plain: bool = True) -> None:
    if not password or len(password) < 8:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres")
    user.hashed_password = hash_password(password)
    user.plain_password = password if store_plain else None
