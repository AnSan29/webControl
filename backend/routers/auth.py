from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from sqlalchemy import or_  # type: ignore

from database import Role, User, get_db
from auth import (
    authenticate_user,
    create_token_pair_for_user,
    decode_token,
    get_current_user,
    get_user_permissions,
    hash_password,
)
from schemas import (
    AuthUserRead,
    LoginResponse,
    RefreshTokenRequest,
    TokenPair,
    UserRegister,
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


def _serialize_auth_user(user: User) -> AuthUserRead:
    return AuthUserRead(
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
        permissions=get_user_permissions(user),
    )


def _issue_token_response(user: User) -> LoginResponse:
    access_token, refresh_token = create_token_pair_for_user(user)
    return LoginResponse(
        token=TokenPair(access_token=access_token, refresh_token=refresh_token),
        user=_serialize_auth_user(user),
    )


def _get_default_role(db: Session) -> Role:
    role = db.query(Role).filter(Role.name == "user").first()
    if not role:
        raise HTTPException(status_code=500, detail="Roles base no han sido inicializados")
    return role


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    existing = (
        db.query(User)
        .filter(or_(User.username == payload.username, User.email == payload.email))
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Usuario o email ya registrado")

    role = _get_default_role(db)
    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role_id=role.id,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _issue_token_response(user)


@router.post("/login", response_model=LoginResponse)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)

    return _issue_token_response(user)


@router.post("/refresh", response_model=TokenPair)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    token_data = decode_token(payload.refresh_token)
    if token_data.get("token_type") != "refresh":
        raise HTTPException(status_code=401, detail="Token de refresco inválido")

    user_id = token_data.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Usuario no disponible")

    access_token, refresh_token = create_token_pair_for_user(user)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=AuthUserRead)
def get_profile(current_user: User = Depends(get_current_user)):
    return _serialize_auth_user(current_user)
