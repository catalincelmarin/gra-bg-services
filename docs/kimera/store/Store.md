# Module `kimera.store.Store`

Lightweight wrapper around PyMongo/MongoEngine connections.

## `Store`

### Constructor
`Store(uri, connection_name='default', **kwargs)` normalises credentials in the URI (percent-encoding username/password when present), sets up a `MongoClient` (deferred connection), and stores the default database name. If `connection_name != '_root'`, it immediately calls `connect()`.

### `connect(self, db=None) -> bool`
Attaches to the specified database (defaults to the current path component), initialises a MongoEngine connection alias, and marks `_connected=True`. Returns the connection state and logs errors via `Helpers.errPrint`.

### `get_databases(self) -> list[str]`
Lists database names available on the server.

### `close(self)`
Closes the underlying `MongoClient`.

### `use(self, collection)`
Returns a `Collection` instance for the requested collection name.
