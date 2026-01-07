# Module `kimera.comm.FastApiWrapper`

Facade around FastAPI that auto-loads routes, sockets, and MCP services from YAML descriptors, and wires supporting middleware.

## `ExceptionMiddleware`
Minimal middleware that catches unhandled exceptions and converts them into HTTP 500 responses.

## `FastAPIWrapper`

### Lifecycle
`FastAPIWrapper()` initialises empty references for the FastAPI app, Socket.IO server, and auth provider.

### Properties
- `app`: The FastAPI instance.
- `sio`: The Socket.IO server (`socketio.AsyncServer`).
- `auth`: Accessor/mutator for the current `BaseAuth` implementation.

### `runApi(self, auth: BaseAuth | None = None)`
Main entry point:
1. Reads `ORIGINS` and `APP_PATH` from the environment (raising if `APP_PATH` is missing).
2. Builds a list of base directories (`<APP_PATH>/app/`) and extension directories discovered under `ext/` and `src/` (only those containing `routes.*.yaml` or `mcp.*.yaml`).
3. Instantiates FastAPI with docs disabled, stores the provided `auth` object.
4. Calls `_setup_middlewares`, `_setup_socket_io`, `_setup_routes_from_yaml`, `_setup_mcp_from_yaml`.
5. Adds custom documentation endpoints and serves static assets from `StoreFactory.get_fstore("_public")` via `setup_public_static`.
6. Returns `self` so callers can access `.app` or `.sio`.

### `_append_extension_paths(self, root_path, folder_paths)`
Searches `app/ext` and `app/src` for directories that contain YAML route or MCP files and appends them to `folder_paths`.

### `_setup_socket_io(self, origins)`
- Creates a Socket.IO ASGI server mounted at `/socket.io/`.
- `connect` event: validates incoming `auth["token"]` via `self._auth.socket_auth`.
- `join_room`: allows clients to join rooms after connection.
- `disconnect`: emits a simple notification.

### `_setup_routes_from_yaml(self, folder_paths)`
Iterates YAML files matching `routes.*.yaml` and passes each to `_process_route_file`.

### `_process_route_file(self, file_path, app)`
- Loads the YAML to obtain `dxs` (module path) and optional `auth` flag.
- Imports the DXS class, instantiates it with the YAML data.
- Registers each route in reverse order (ensuring appended routes override defaults) with FastAPI, applying auth dependencies when requested.
- Configures socket routes defined under the `sockets` array by binding Socket.IO event names to async handlers that JSON-parse payloads when possible.

### `_setup_mcp_from_yaml(self, folder_paths)`
Locates `mcp.*.yaml` files and processes them via `_process_mcp_file`.

### `_process_mcp_file(self, file_path, app)`
- Reads server metadata and module path under `mcp`.
- Imports the MCP class and instantiates it, resolving relative directories for `tools`, `prompts`, and `resources` via `_resolve_dir`.
- Registers each route in `instance.default_routes`, optionally enforcing auth through `Depends(self._auth.get_auth)`.

### Documentation helpers
- `_setup_custom_docs(self)`: Re-enables Swagger UI and ReDoc at `/docs` and `/redoc` using CDN assets, and mounts the OAuth2 redirect route.

### Static assets
- `setup_public_static(self, route="", path="", html=False)`: Mounts a `StaticFiles` app rooted at the `_public` file store.

### Middleware
`_setup_middlewares(self, origins)` adds CORS middleware and an HTTP middleware that:
- Extracts bearer tokens from `Authorization` headers and stores them in `request.state.token`.
- Removes automatic `Access-Control-Allow-Origin` headers for Socket.IO responses to let Socket.IO manage CORS.

`ExceptionMiddleware` is defined but commented out; projects can enable it if desired.
