# Module `kimera.store.AutoRepo`

MongoEngine implementation of `BaseRepo` that maps Pydantic schemas to documents automatically.

## `AutoRepo(schema_cls, model_cls)`
- Inherits `BaseRepo`, connecting to the Mongo alias declared on the MongoEngine model (`model_cls._meta['db_alias']`).
- Uses `schema_cls` for validation/serialisation.

### `create(self, obj_data)`
Validates via `schema_cls`, instantiates the MongoEngine model, saves it, and returns `new_obj.to_dict()`.

### `all(self)`
Returns a list of `to_dict()` representations for every document.

### `update(self, id, obj_data)`
Loads the document by `ObjectId`, applies the validated fields (`exclude_unset=True`), saves, and returns `to_dict()`.

### `delete(self, id)`
Removes the document, raising `HTTPException(404)` when not found.

### `one(self, id)`
Returns `to_dict()` for the matching document.

### `findOne(self, **kwargs)` / `getOne(self, **kwargs)`
Query helpers returning either a dict (`findOne`) or raw MongoEngine object (`getOne`).

### `find(self, **kwargs)`
Returns a list of dicts for documents matching the filter.
