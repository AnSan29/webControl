from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field


# ========================
# Role Schemas
# ========================

class RoleBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = Field(default=None, max_length=500)


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3, max_length=50)
    description: Optional[str] = Field(default=None, max_length=500)


class RoleRead(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime


# ========================
# User Schemas
# ========================

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role_id: Optional[int] = None  # Hacer opcional
    site_id: Optional[int] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    # Permitir usar role (string) como alternativa a role_id
    role: Optional[str] = None  # Agregar esta línea


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    role_id: Optional[int] = None
    role: Optional[str] = None  # Permitir actualizar por nombre de rol
    site_id: Optional[int] = Field(default=None)
    is_active: Optional[bool] = None


class UserPasswordUpdate(BaseModel):
    password: str = Field(..., min_length=8, max_length=128)


class UserRead(UserBase):
    id: int
    role_name: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ========================
# Site Assignment Schemas
# ========================

class SiteAssignmentBase(BaseModel):
    site_id: int
    user_id: int
    permission: str = Field(default="editor", pattern=r"^(owner|editor|viewer)$")


class SiteAssignmentCreate(SiteAssignmentBase):
    pass


class SiteAssignmentRead(SiteAssignmentBase):
    id: int
    created_at: datetime


# ========================
# Auth Schemas
# ========================

class TokenPayload(BaseModel):
    sub: str
    token_type: str
    exp: int


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class AuthUserRead(UserRead):
    permissions: List[str] = Field(default_factory=list)


class LoginResponse(BaseModel):
    token: TokenPair
    user: AuthUserRead


# ========================
# Site creation helper
# ========================

class OwnerCredentials(BaseModel):
    username: str
    email: EmailStr
    temporary_password: str
    role: str = Field(default="owner")


class SiteWithOwnerResponse(BaseModel):
    id: int
    name: str
    message: str
    owner_credentials: OwnerCredentials
