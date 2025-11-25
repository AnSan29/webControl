"""Pydantic schemas shared by the API.

This module intentionally focuses on the user-management payloads used by
`backend.main`.  It replaces the previously-empty `backend.schemas` stub so
that the FastAPI endpoints can rely on strong typing and validation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, Field, field_validator

ALLOWED_INTERNAL_EMAIL_DOMAINS = {"owners.webcontrol.local"}


def _normalize_email(value: str) -> str:
    value = (value or "").strip()
    if not value:
        raise ValueError("Email requerido")

    domain = value.split("@")[-1].lower() if "@" in value else ""
    try:
        return validate_email(
            value,
            allow_smtputf8=True,
            check_deliverability=False,
        ).email
    except EmailNotValidError as exc:
        if domain in ALLOWED_INTERNAL_EMAIL_DOMAINS:
            return value
        raise ValueError(str(exc)) from exc


def _normalize_optional_email(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return _normalize_email(value)


class RoleBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = None


class RoleRead(RoleBase):
    id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[str] = Field(default=None, min_length=3, max_length=255)
    site_id: Optional[int] = None
    role_id: Optional[int] = None
    is_active: bool = True
    avatar_url: Optional[str] = Field(default=None, max_length=500)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_email(value)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    role: Optional[str] = None
    expires_at: Optional[datetime] = None


class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    email: Optional[str] = None
    site_id: Optional[int] = None
    role_id: Optional[int] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)
    avatar_url: Optional[str] = Field(default=None, max_length=500)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_email(value)


class UserPasswordUpdate(BaseModel):
    password: str = Field(..., min_length=8, max_length=128)


class UserRead(UserBase):
    id: int
    role_name: Optional[str] = None
    site_name: Optional[str] = None
    last_login: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class UserDetailRead(UserRead):
    password_plain: Optional[str] = None


__all__ = [
    "RoleBase",
    "RoleRead",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserPasswordUpdate",
    "UserRead",
    "UserDetailRead",
]
