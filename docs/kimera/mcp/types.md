# Module `kimera.mcp.types`

Pydantic models representing MCP responses and error structures.

## `MCPError`
- Fields: `code: int`, `message: str`, `data: Any | None`.

## `MCPTextItem`
- Fields: `type: str` (default `"text"`), `text: str`.

## `MCPResource`
- Fields: `uri: str`, `text: str`, `mimeType: str` (default `"application/json"`).

## `MCPResponse`
- Fields: `jsonrpc: str` (default `"2.0"`), `id: int | str | None`, `result: dict | list | None`.
- `success(req_id, result)`: classmethod returning a dict form of a successful response.
- `failure(req_id, code, message, data=None)`: classmethod returning an error payload (delegates to `MCPError`).
- `to_json()`: Serialises the model to JSON.
