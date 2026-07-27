"""FastAPI dependency providers.

Re-exports get_db_session for use in routers.
Feature-specific dependencies live in submodules of this package.
"""

from app.core.database import get_db_session

__all__ = ["get_db_session"]
