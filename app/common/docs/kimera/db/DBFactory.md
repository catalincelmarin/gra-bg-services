# Module `kimera.db.DBFactory`

Lazy registry that loads database connections defined in YAML files bundled with the app.

## Class attributes
- `_instances`: connection_name → `Database` instance.

## API
- `get_db(connection_name, uri=None, **kwargs)`: Returns a cached `Database`, optionally creating it if `uri` is provided.
- `close_db(connection_name)`: Removes the cached database and closes its connection.
- `load_dbs(dbs_path: str)`: Walks `<dbs_path>/app/**/dbs*.yaml`, reads `dbs:` sections, pulls connection URIs from environment variables, and registers `Database` instances via `get_db`.

`load_dbs` prints `NO URI` when a configuration entry lacks an environment variable. On success the YAML-defined databases become available to `StoreFactory` and repository classes.
