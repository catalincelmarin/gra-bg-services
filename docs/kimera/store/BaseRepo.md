# Module `kimera.store.BaseRepo`

Abstract MongoDB repository base that looks up stores via `StoreFactory`.

## `BaseRepo`

### Constructor
`BaseRepo(connection_name="_root")` fetches an existing `Store` instance from `StoreFactory`.

### Utilities
- `connect(self, db)`: Ensures the underlying `Store` is connected to the specified database.
- `use(self, collection) -> pymongo.collection.Collection`: Returns a PyMongo collection handle.

### Abstract CRUD methods
Subclasses must override:
- `create(obj_data)`
- `get(id)`
- `find(**filters)`
- `update(id, obj_data)`
- `delete(id)`

All methods are expected to return JSON-serialisable payloads.
