# Module `kimera.db.AutoWireRepo`

Asynchronous repository base for SQLAlchemy models that are reflected via automap.

## `AutoWireRepo`

### Class attributes
- `model_name`: **required** name of the automapped model (set on subclasses).
- `store_name`: name of the registered relational store (`StoreFactory.get_rdb_store`). Defaults to `"default"` but can be overridden.

### Constructor
Validates that `model_name` is provided, pulls the configured database instance from `StoreFactory`, and defers model resolution until `connect()` is called.

### `get_class(self, table_name: str)`
Utility that searches `db._Base.classes` for a case-insensitive match and returns the mapped class or raises `AttributeError`.

### `async connect(self)`
- Establishes the database connection (creating engine/session if needed).
- Validates that automap metadata includes `model_name` and binds it to `self.model`.

### CRUD surface
Each method asserts that `self.model` has been resolved (via `_require_model`). All operations run within `async with self.db.session() as session`:
- `async all(self) -> list`
- `async get(self, id)`
- `async find(self, **filters) -> list`
- `async create(self, **fields) -> Any`
- `async update(self, id, **fields) -> Any | None`
- `async delete(self, id) -> bool`
- `async create_many(self, rows: Sequence[dict]) -> list`

Sessions are opened with `expire_on_commit=False`, so returned objects remain usable after the context exits.
