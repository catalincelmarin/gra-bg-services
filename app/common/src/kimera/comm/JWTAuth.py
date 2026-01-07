from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from fastapi import HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader

from kimera.comm.BaseAuth import BaseAuth

# Define schemes here (kept out of the abstract base)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
api_key_scheme = APIKeyHeader(name="Authorization")


class JWTAuth(BaseAuth):
    """
    Concrete JWT-based auth with optional API-key fallback.
    - Bearer: Authorization: Bearer <jwt>
    - API key: Authorization: Api-Key <key>   (or just the raw key)
    """

    ADMIN_ROLE_VALUE = "admin"

    def __init__(self):
        super().__init__()

    # --- config props ---
    @property
    def SECRET_KEY(self) -> str:
        return self._SECRET_KEY

    @property
    def ALGORITHM(self) -> str:
        return self._ALGORITHM

    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        return self._ACCESS_TOKEN_EXPIRE_MINUTES

    # --- public API ---
    async def socket_auth(self, token: str) -> Dict[str, Any]:
        try:
            payload = self.decode_token(token)
            return payload
        except Exception:
            # Keep errors terse for WS
            raise ConnectionRefusedError("authentication failed")

    async def get_auth(self, request: Request) -> Dict[str, Any]:
        credentials_exc = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        token: Optional[str] = None
        api_key: Optional[str] = None

        # Try Bearer first
        try:
            token = await oauth2_scheme(request)
        except HTTPException as e:
            if e.status_code == status.HTTP_401_UNAUTHORIZED:
                # Fallback to API key header
                try:
                    api_key = await api_key_scheme(request)
                except HTTPException:
                    api_key = None

        if token:
            try:
                return self.decode_token(token)
            except HTTPException:
                raise credentials_exc

        if api_key:
            user = await self.resolve_api_key(api_key)
            if user and isinstance(user, dict):
                return user
            raise credentials_exc

        raise credentials_exc

    def create_access_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta if expires_delta else timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def decode_token(self, token: str) -> Dict[str, Any]:
        try:
            return jwt.decode(token.strip(), self.SECRET_KEY, algorithms=[self.ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

    async def resolve_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Override to implement your API-key lookup.
        Example parsing supports:
          - "Api-Key <key>"
          - "Token <key>"
          - "<key>"
        Return a user dict like {"id": ..., "email": ..., "role": ...} or None.
        """
        # Example skeleton:
        # raw = api_key.split()[-1] if " " in api_key else api_key
        # user = await Users().check_api_key(raw)  # your own async store
        # return user
        return None

