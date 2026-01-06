# Module `kimera.helpers.Hook`

Defines a reusable webhook client abstraction with optional bearer-token handshakes.

## `Hook`
Abstract base class for outbound HTTP hooks.

### Constructor
`__init__(self, url: str, method: str, auth: dict | None)`
- `url`: Base endpoint to call.
- `method`: HTTP verb (`GET` or `POST`).
- `auth`: Optional dict describing an authentication flow. When `type` is `"Bearer"`, the hook performs a one-time token fetch by POSTing to `auth["url"]` with body `auth["auth"]`, then caches the field referenced by `auth["extract"]`.

### Invocation
`__call__(self, data: dict | None) -> Any`
- Applies any cached bearer token to the `Authorization` header.
- If `data` is supplied, appends it as a query string for GET requests or JSON body for POST requests (defaults to `{"data": None}` when `None`).
- Returns decoded JSON when the response advertises `application/json`; otherwise returns the text payload.
- On non-200 responses, returns the status code so callers can decide how to react.
- Logs hook-authentication failures via `Helpers.sysPrint`.

### Extension point
`run(self, result)` is declared `@abstractmethod`. Concrete hooks implement this to define how the response `result` should be consumed by the application.
