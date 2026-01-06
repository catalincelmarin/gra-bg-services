# Module `kimera.db.Database`

Async SQLAlchemy database wrapper that supports dynamic schema reflection and scoped sessions per asyncio task.

## `Database`

### Constructor
`Database(uri: str | None = None, connection_name: str = "default", **kwargs)` sets up lazy attributes (`_engine`, `_session`, `_metadata`, `_Base`, `_inspector`, `_connected`).

### `async connect(self, db: str | None = None) -> bool`
- Optionally switches the database portion of the URI before connecting.
- Creates an async engine with pool size 50 / max overflow 10.
- Within an async transaction:
  - Calls `_sync_reflection` in a thread-safe context to populate metadata and automap base.
  - Executes `SELECT 1` to verify connectivity and mark `_connected = True`.
- Configures an `async_scoped_session` bound to `asyncio.current_task`.
- Returns the connection status and logs failures via `Helpers.errPrint`.

### `_sync_reflection(self, sync_conn)`
Runs in sync context to reflect metadata, prepare the automap base, and attach a SQLAlchemy inspector.

### `async exec(self, sql: str)`
Executes raw SQL text against the engine and returns the result or an error string describing the failure.

### `async switch_db(self, db_name: str)`
Closes the current engine (if connected) and rebuilds the URI with the provided db name, then reconnects.

### `async create(self, db: str) -> bool`
Executes `CREATE DATABASE <db>` on the current engine, returning `True` on success.

### `async close(self)`
Disposes of the engine to release resources.

### Properties
- `session`: callable producing an `AsyncSession` context manager; intended for `async with database.session() as session` usage.
