# Module `kimera.mcp.CommonMCP`

Default implementation of an MCP server that wires the config gathered by `BaseMCP` into the standard MCP JSON-RPC endpoints.

## `CommonMCP`

### Constructor
Delegates to `BaseMCP` to load tools/prompts/resources and preserves `_default_routes`.

### `default_routes`
Property returning the base route list (currently a single POST `/` endpoint).

### `async on_root(self, body)`
Entry point for MCP RPC requests. Dispatches on `body["method"]` and calls the corresponding handler. Supported methods:
- `initialize`
- `tools/list`
- `prompts/list`
- `resources/list`
- `resources/templates/list`
- `tools/call`
- `prompts/get`
- `resources/read`
Unknown methods return an `MCPError` with code `-32600`.

### `async initialize(self, body)`
Validates request shape, emits aggregated tool definitions and resource templates, and returns `MCPResponse(result=server_config)`.

### `async tools_list(self, body)`
Returns all tool definitions gathered from configuration.

### `async prompts_list(self, body)`
Returns prompt definitions.

### `async resources_templates_list(self, body)`
Flattens the `templates` arrays declared under each resource config.

### `async resources_list(self, body)`
Returns resource definitions.

### `async tools_call(self, body)`
Looks up the handler name in `_bounded_tools` using `params.name`. If the method exists on the instance it is awaited, otherwise falls back to `default_call`. The return object is converted into MCP text items for `content` and `output`.

### `async prompts_call(self, body)`
Invokes the prompt handler mapped under `_bounded_tools` (likely a typo in the original code—handlers are stored alongside tools). Packs the result into an `MCPTextItem` response.

### `async resources_read(self, body)`
Parses the `params.uri`, splitting query parameters via `MCPHelpers.querystring_to_dict`, and invokes the resource handler registered under `_bounded_resources`. Returns a list of `MCPResource` payloads.

### `async default_call(self, *args, **kwargs)`
Fallback handler that simply echoes arguments.
