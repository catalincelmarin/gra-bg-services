# Module `kimera.dxs.CommonDXS`

Mixin-level implementation for general-purpose DXS endpoints.

## `CommonDXS`

### Constructor
`CommonDXS(method_config: dict)` augments the base config with default routes when the resource flag is enabled.
- Injects a default GET `/` route mapped to `init`.
- When `method_config["resource"]` is truthy, the final route list becomes `default_routes + method_config['routes']` (if any). Otherwise preserves the provided list.

The class is intended to be subclassed further; actual HTTP method implementations (e.g., `init`) are left to concrete DXS classes.
