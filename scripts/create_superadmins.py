"""Utility script to ensure required superadmin accounts exist."""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.auth import hash_password
from backend.database import SessionLocal, User, Role, init_db
from backend.services.user_service import generate_unique_email

SUPERADMIN_ROLE_NAME = "superadmin"
DEFAULT_DOMAIN = os.getenv("SUPERADMIN_EMAIL_DOMAIN", "webcontrol.com")

USERS_TO_ENSURE = [
    {
        "username": "andres",
        "email": os.getenv("ANDRES_EMAIL", "andres@webcontrol.com"),
        "password": os.getenv("ANDRES_PASSWORD", "Andres#2024"),
    },
    {
        "username": "dilan",
        "email": os.getenv("DILAN_EMAIL", "dilan@webcontrol.com"),
        "password": os.getenv("DILAN_PASSWORD", "Dilan#2024"),
    },
]


def _get_superadmin_role(session) -> Role:
    role = session.query(Role).filter(Role.name == SUPERADMIN_ROLE_NAME).first()
    if not role:
        raise RuntimeError("No existe el rol superadmin en la base de datos")
    return role


def _normalize_email(session, username: str, desired_email: str | None) -> str:
    email = (desired_email or "").strip()
    if email:
        return email
    return generate_unique_email(session, username, domain=DEFAULT_DOMAIN)


def ensure_superadmin(session, username: str, email: str | None, password: str) -> str:
    role = _get_superadmin_role(session)
    normalized_email = _normalize_email(session, username, email)
    user = session.query(User).filter(User.username == username).first()

    if user:
        user.email = normalized_email
        user.role_id = role.id
        user.is_active = True
        if password:
            user.hashed_password = hash_password(password)
            user.plain_password = password
        if not user.activated_at:
            user.activated_at = datetime.utcnow()
        action = "actualizado"
    else:
        if not password:
            raise RuntimeError(f"Debes definir una contraseña para {username}")
        user = User(
            username=username,
            email=normalized_email,
            role_id=role.id,
            is_active=True,
            activated_at=datetime.utcnow(),
        )
        user.hashed_password = hash_password(password)
        user.plain_password = password
        session.add(user)
        action = "creado"

    session.commit()
    return action


def main() -> None:
    init_db()
    session = SessionLocal()
    try:
        for data in USERS_TO_ENSURE:
            username = data["username"].strip().lower()
            password = data.get("password")
            email = data.get("email")
            action = ensure_superadmin(session, username, email, password)
            print(f"✅ Usuario {username} {action}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
