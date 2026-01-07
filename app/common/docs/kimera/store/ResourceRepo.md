# Module `kimera.store.ResourceRepo`

MongoEngine-backed repository implementing CRUD with optional password hashing.

## `ResourceRepo(schema_cls, model_cls)`
- Builds on `BaseRepo`, using `model_cls._meta['db_alias']` to fetch the correct Mongo connection.
- `collection` caches the target Mongo collection (via PyMongo) but operations are executed with MongoEngine documents.

### `create(self, obj_data)`
Validates via `schema_cls`, hashes `password` if present, saves a new document, and returns the generated string id. Duplicate keys raise `HTTPException(404)` with error details.

### `all(self)`
Returns a list of serialised documents (`{"id": str(obj.id), ...}`) using `schema_cls(**obj.to_mongo()).model_dump()`.

### `update(self, id, obj_data)`
Fetches the document by `ObjectId`, rehashes `password` when provided, saves, and returns the updated schema dump.

### `delete(self, id)`
Removes the document; raises 404 if missing.

### `one(self, id)`
Returns the serialised document or raises 404.

### `findOne(self, **kwargs)` / `getOne(self, **kwargs)` / `find(self, **kwargs)`
Convenience queries to fetch a single / raw / list of documents. `findOne` wraps the schema dump with the document id, whereas `getOne` returns the MongoEngine object directly.
