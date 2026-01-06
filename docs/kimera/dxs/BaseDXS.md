# Module `kimera.dxs.BaseDXS`

Abstract base for dynamically loaded DXS resources.

## `BaseDXS`

### Constructor
`BaseDXS(method_config: dict)` extracts common configuration:
- `base_space`: logical namespace for mounting (unused in code but available to subclasses).
- `url_space`: appended to the FastAPI route path.
- `routes`: a list of route descriptors; defaulted to `[]` if missing.
- `token`: placeholder for future auth tokens.

### Properties
- `path -> str`: Returns `f"/{self.url_space}"`, used by routers.
- `routes -> list[dict]`: Accessor for the configured route list. Subclasses mutate `_routes` to inject defaults.
