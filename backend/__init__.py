"""Backend package bootstrap helpers."""

from . import api_schemas as _api_schemas
import sys as _sys

# Mantener compatibilidad con módulos que sigan importando backend.schemas
_sys.modules.setdefault(f"{__name__}.schemas", _api_schemas)

__all__ = ["_api_schemas"]
