# Module `kimera.comm.JWTAuth`

Concrete implementation of `BaseAuth` built on JWT bearer tokens with optional API-key fallback.

## `JWTAuth`

### Properties
Expose the inherited configuration fields (`SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`).

### `async socket_auth(self, token)`
Decodes the JWT and returns its payload or raises `ConnectionRefusedError` to reject the connection.

### `async get_auth(self, request)`
- Attempts to extract a bearer token via FastAPI's `OAuth2PasswordBearer` flow.
- Falls back to reading an `Authorization` header via `APIKeyHeader`.
- For tokens, decodes and returns the payload, raising `HTTPException(401)` on failure.
- For API keys, calls `resolve_api_key` (default implementation returns `None`).

### `create_access_token(self, data, expires_delta=None)`
Creates a signed JWT with an `exp` claim. Defaults to the configured expiry minutes.

### `decode_token(self, token)`
Validates signature and expiration, raising `HTTPException` for invalid/expired tokens.

### `async resolve_api_key(self, api_key)`
Stub for projects to override—expected to map API keys to user dicts. The default implementation returns `None` (i.e., API-key auth disabled unless customised).
