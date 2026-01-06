# Module `kimera.store.FileStore`

Path helper for static assets or file-based storage.

## `LocalFileStore(path, **kwargs)`
- Stores `path` as both `_path` and `_base_path`.
- `path(route="/")`: joins the base path with an optional route segment.
- `base_path(route="/")`: same as `path`, retained for semantic clarity.
