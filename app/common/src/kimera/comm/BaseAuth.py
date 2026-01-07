from __future__ import annotations

import os
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Optional, Dict

from fastapi import Request


class BaseAuth(ABC):
    """
    Abstract auth contract. Implement in a concrete class (e.g., JWTAuth).
    """

    def __init__(self):
        self._SECRET_KEY = os.getenv("JWT_SALT", "your-secret-key-is-not-safe-with-me")
        self._ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        self._ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE", 60 * 100))  # 100 hours

    # --- required configuration ---
    @property
    @abstractmethod
    def SECRET_KEY(self) -> str: ...

    @property
    @abstractmethod
    def ALGORITHM(self) -> str: ...

    @property
    @abstractmethod
    def ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int: ...

    # --- required behaviors ---
    @abstractmethod
    async def socket_auth(self, token: str) -> Dict[str, Any]: ...

    @abstractmethod
    async def get_auth(self, request: Request) -> Dict[str, Any]: ...

    @abstractmethod
    def create_access_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str: ...

    @abstractmethod
    def decode_token(self, token: str) -> Dict[str, Any]: ...

    @abstractmethod
    async def resolve_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Given the raw API key header value (e.g. "Api-Key abc123" or "abc123"),
        return a user dict if valid, else None.
        """
        ...
