# Module `kimera.mcp.BaseMCP`

Abstract foundation for MCP (Model Context Protocol) servers.

## `BaseMCP`

### Constructor
`BaseMCP(server_config, tools_config=None, prompts_config=None, resources_config=None)`:
- Stores basic metadata (`base_space`, `url_space`, `server_config`).
- Scans the directories pointed to by `tools_config["dir"]`, `prompts_config["dir"]`, and `resources_config["dir"]` for YAML files named `tools.*.yaml`, `prompts.*.yaml`, and `resources.*.yaml`.
- Aggregates tool/prompt/resource definitions into `_tools_config`, `_prompts_config`, `_resources_config`.
- Builds dictionaries (`_bounded_tools`, `_bounded_prompts`, `_bounded_resources`) that map definition names/URIs to handler method names declared in the YAML.
- Prepares `default_routes` (currently only `POST /` → `on_root`).

### Properties
- `path`: Returns `f"/{self.url_space}"`, used when mounting routes.
- `routes`: Returns `_default_routes`.
- `server_config`: Exposes the raw server metadata (e.g., `{ "name": ..., "version": ... }`).

### Abstract hooks
Concrete MCP servers must implement the following async methods:
- `initialize(body)`
- `tools_list(body)`
- `prompts_list(body)`
- `resources_list(body)`
- `tools_call(body)`
- `resources_read(body)`
- `on_root(body)` (entry point for MCP requests)
- `default_call(*args, **kwargs)` (fallback when a tool has no explicit handler)

Implementations can leverage `_bounded_tools`, `_bounded_prompts`, and `_bounded_resources` to look up handlers specified in configuration.
