# Module `kimera.mcp.MCPHelpers`

Utility functions for parsing query strings used by MCP resource endpoints.

## `MCPHelpers`

### `_is_int_str(s: str) -> bool`
Regex-backed helper to detect integer-like strings (optional leading `-`).

### `_coerce_scalar(v: str)`
Normalises scalar strings into native Python types where reasonable:
- `"true"`/`"false"` → booleans.
- `"null"` → `None`.
- Empty string → `""`.
- Int-like strings → `int`.
- Naïve float detection (`"."` in string) converts to `float`.
Otherwise returns the original string.

### `_insert_path(root: dict, parts: list[str], value: str)`
Builds a nested dict structure given key parts from a query-string token (e.g., `filters[$and][0][name]`). Numeric parts are kept as string keys.

### `_normalize(node)`
Recursively converts dicts whose keys are contiguous integer strings (`"0".."n"`) into actual Python lists. Called after `_insert_path` to produce JSON-like structures.

### `querystring_to_dict(qs: str) -> dict`
High-level helper used by `CommonMCP.resources_read`:
1. Parses the query string into `(key, value)` pairs via `urllib.parse.parse_qsl`.
2. Breaks bracket notation into parts and builds a dict-only tree with `_insert_path`.
3. Normalises array-like dicts into lists with `_normalize`.
Returns a nested dict/list structure mirroring the original Strapi-style query string.
