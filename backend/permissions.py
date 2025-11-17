"""Permisos y utilidades para control de acceso basado en roles."""
from __future__ import annotations

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:  # Evita dependencias circulares en tiempo de ejecución
    from database import Site, User

ROLE_PERMISSIONS = {
    "admin": [
        "sites:read",
        "sites:write",
        "sites:publish",
        "users:read",
        "users:write",
        "roles:manage",
        "stats:view",
    ],
    "owner": [
        "sites:read:own",
        "sites:write:own",
        "sites:publish:own",
        "stats:view:own",
    ],
    "editor": [
        "sites:read:assigned",
        "sites:write:assigned",
    ],
    "user": [
        "dashboard:view",
    ],
}


def get_permissions_for_role(role_name: str | None) -> List[str]:
    return ROLE_PERMISSIONS.get(role_name or "", [])


def is_admin(user: "User") -> bool:
    return bool(user and user.role and user.role.name == "admin")


def is_owner(user: "User", site: "Site" | None) -> bool:
    return bool(user and site and user.site_id == site.id)


def is_editor(user: "User", site: "Site" | None) -> bool:
    if not (user and site):
        return False
    return any(assignment.site_id == site.id for assignment in getattr(user, "site_assignments", []))


def can_view_site(user: "User", site: "Site" | None) -> bool:
    if site is None:
        return False
    return is_admin(user) or is_owner(user, site) or is_editor(user, site)


def can_edit_site(user: "User", site: "Site" | None) -> bool:
    if site is None:
        return False
    if is_admin(user):
        return True
    if is_owner(user, site):
        return True
    return is_editor(user, site)


def can_publish_site(user: "User", site: "Site" | None) -> bool:
    if site is None:
        return False
    if is_admin(user):
        return True
    if is_owner(user, site):
        return True
    return False


def can_manage_users(user: "User") -> bool:
    return is_admin(user)


def can_manage_roles(user: "User") -> bool:
    return is_admin(user)
