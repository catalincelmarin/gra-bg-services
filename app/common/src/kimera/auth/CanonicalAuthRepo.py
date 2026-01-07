from __future__ import annotations

import importlib
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional
from pydantic import EmailStr


class CanonicalAuthRepo(ABC):
    def __init__(self, auto_wire_module,**kwargs):
        """
        Dynamically import a module and load its `AutoWire` class.

        Example:
            AuthRepo("kimera.store.AutoWireRepo")
        """
        module_name, class_name = auto_wire_module.rsplit(".", 1)
        module = importlib.import_module(module_name)
        AutoWireClass = getattr(module, class_name)
        self.auto_wire = AutoWireClass(**kwargs)
    # ----- Utility primitives -----
    @staticmethod
    @abstractmethod
    def _now() -> datetime:
        """Return current datetime."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _make_token() -> str:
        """Generate a secure random token."""
        raise NotImplementedError

    # ----- Core operations -----
    @abstractmethod
    def register(
        self,
        email: EmailStr,
        password: str,
        name: Optional[str] = None,
        role: str = "user"
    ) -> Any:
        """Create a new user or refresh activation if already registered but inactive."""

    @abstractmethod
    def login(self, email: EmailStr, password: str) -> Optional[dict[str, Any]]:
        """Authenticate user by email and password."""

    @abstractmethod
    def activate(self, token: str) -> bool:
        """Activate a user account by activation token."""

    @abstractmethod
    def start_password_reset(self, email: str) -> Optional[str]:
        """Initiate password reset and return the reset token."""

    @abstractmethod
    def finish_password_reset(self, token: str, new_password: str) -> bool:
        """Complete password reset using a valid token."""

    @abstractmethod
    def oauth_login(self, provider: str, provider_payload: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Handle OAuth login or linking flow."""
