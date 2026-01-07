# Module `kimera.helpers.Auth`

Legacy JWT helper (superseded in new code by `kimera.comm.JWTAuth`). Provides barebones FastAPI dependencies.

## `Auth`

### Constructor
Initialises JWT defaults from environment:
- `SECRET_KEY`: `SALT` env (fallback `"your-secret-key-is-not-safe-with-me"`).
- `ALGORITHM`: Hard-coded `HS256`.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: 100 hours.

### `socket_auth(self, token: str) -> dict`
Async static helper for Socket.IO handshake validation. Decodes the JWT and raises `ConnectionRefusedError` on failure.

### `get_auth(self, request: Request) -> dict`
FastAPI dependency that accepts either an OAuth2 bearer token or, as a fallback, an API key in the same header. Steps:
1. Try extracting an OAuth2 bearer token via FastAPI's `OAuth2PasswordBearer` dependency.
2. If missing, read the `Authorization` header via `APIKeyHeader`.
3. Decode the JWT (`jwt.decode`) and verify it contains a `data` payload.
4. Maps role `22222` to `isAdmin=True`.
Raises `HTTPException(401)` on invalid or expired credentials.

### `create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str`
Signs JWTs with `HS256`. Injects an `exp` claim using `expires_delta` (default: 120 minutes from now).

### `decode_token(self, token: str) -> dict`
Decodes a JWT and validates signature/expiry. Raises `HTTPException(401)` on failure.
