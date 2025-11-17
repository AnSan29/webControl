"""Routers del proyecto webControl."""

from .auth import router as auth_router  # noqa: F401
from .roles import router as roles_router  # noqa: F401
from .users import router as users_router  # noqa: F401

__all__ = [
	"auth_router",
	"roles_router",
	"users_router",
]
