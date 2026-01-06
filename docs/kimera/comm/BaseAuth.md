# Module `kimera.comm.BaseAuth`

Abstract interface describing how authentication providers integrate with Kimera services.

## `BaseAuth`

### Constructor
Reads defaults from environment:
- `JWT_SALT` (default `"your-secret-key-is-not-safe-with-me"`).
- `JWT_ALGORITHM` (default `HS256`).
- `JWT_EXPIRE` (minutes; default `6000`).

### Required properties
Subclasses must expose:
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

### Required behaviours
- `async socket_auth(self, token) -> dict`: Validate WebSocket authentication requests.
- `async get_auth(self, request: Request) -> dict`: FastAPI dependency returning the authenticated user.
- `create_access_token(self, data, expires_delta=None) -> str`: Issue a signed token.
- `decode_token(self, token) -> dict`: Validate/parse a token.
- `async resolve_api_key(self, api_key) -> dict | None`: Optional API-key fallback (return user dict when valid).
