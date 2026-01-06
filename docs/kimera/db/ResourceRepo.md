# Module `kimera.db.ResourceRepo`

SQLAlchemy-backed implementation of `BaseRepo` that uses a Pydantic schema to validate inputs/outputs.

## `ResourceRepo(schema_cls, model_cls, db)`
- `schema_cls`: Pydantic model with `model_dump`/`from_orm` support.
- `model_cls`: SQLAlchemy ORM class.
- `db`: SQLAlchemy `Session` (synchronous) used for all operations.

### `create(self, obj_data) -> str`
Validates payload via `schema_cls`, hashes passwords (if attribute present), persists a new ORM instance, and returns its stringified primary key. Database errors raise `HTTPException(500)`.

### `all(self) -> list[dict]`
Fetches and serialises all rows via `schema_cls.from_orm(...).model_dump()`.

### `update(self, id, obj_data) -> dict`
Looks up the record, applies field updates (rehashing passwords as needed), commits, and returns the serialised object. Missing rows raise 404.

### `delete(self, id) -> bool`
Deletes the row; missing IDs raise 404.

### `one(self, id) -> dict`
Retrieves a single row and returns it as a dict, raising 404 if absent.
