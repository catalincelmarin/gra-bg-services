# Module `kimera.auth.CanonicalAuthRepo`

Abstract base class for authentication repositories that dynamically wire a datastore adapter (e.g., AutoWire repos).

## `CanonicalAuthRepo`

### Constructor
`CanonicalAuthRepo(auto_wire_module: str, **kwargs)` imports the specified module path (e.g., `kimera.store.AutoRepo.AutoRepo`), instantiates the `AutoWire` class, and stores it on `self.auto_wire`. Extra keyword args are forwarded to the AutoWire constructor.

### Required static utilities
Subclasses must implement:
- `_now() -> datetime`: Current timestamp helper.
- `_make_token() -> str`: Secure token generator used for activation/reset flows.

### Repository interface
Concrete implementations must provide:
- `register(email, password, name=None, role="user")`
- `login(email, password)`
- `activate(token)`
- `start_password_reset(email)`
- `finish_password_reset(token, new_password)`
- `oauth_login(provider, provider_payload)`

Each method should leverage `self.auto_wire` to access persistence primitives.
