"""Import legado para endpoints que ainda usam este modulo."""

from backend.core.security import get_current_user

__all__ = ["get_current_user"]
