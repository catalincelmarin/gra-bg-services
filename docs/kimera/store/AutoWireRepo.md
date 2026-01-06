# Module `kimera.store.AutoWireRepo`

MongoEngine repository with additional error handling and aggregation helpers. Unlike `AutoRepo`, it focuses on direct document manipulation without schema validation.

## Custom exceptions
- `RepoError`: base class.
- `RepoBadRequest`: malformed inputs (e.g., bad ObjectId, invalid pipeline).
- `RepoNotFound`: lookup failures.
- `RepoConflict`: duplicate-key conflicts.
- `RepoValidationError`: MongoEngine validation failures.

## `AutoWireRepo(model_cls)`
- Inherits `BaseRepo`, binding to the Mongo alias/collection declared on the MongoEngine model.

### Helpers
- `_oid(id_str)`: Validates and converts a string into `ObjectId`, raising `RepoBadRequest` if invalid.
- `_get_by_id(id_str)`: Loads a document or raises `RepoNotFound`.
- `_normalize(value)`: Recursively converts Mongo types (`ObjectId`, `datetime`, nested structures) to JSON-friendly primitives—used by aggregation results.

### CRUD
- `create(obj_data)`: Instantiates and saves `model_cls(**obj_data)`, raising conflict/validation-specific exceptions.
- `get(id)`: Returns `to_dict()` for the document with the given id.
- `find(skip=0, limit=50, order_by=None, **filters)`: Provides pagination and ordering, returning `to_dict()` representations.
- `update(id, obj_data)`: Applies whitelisted fields (ignores unknown fields and id) and saves; conflict/validation exceptions preserved.
- `delete(id)`: Removes the document and returns `True`.

### Aggregation
- `run_aggregation(pipeline)`: Executes a raw MongoDB aggregation pipeline on the underlying collection, normalising the results for JSON serialisation. Non-list pipelines raise `RepoBadRequest`.
