# Module `kimera.dxs.ResourceDXS`

Resource-oriented DXS that autowires a repository for CRUD operations and secures endpoints with JWT authentication.

## `ResourceDXS`

### Constructor
`ResourceDXS(method_config: dict)`:
- Calls `BaseDXS` to prime shared config.
- Defines default CRUD routes (`find`, `findOne`, `create`, `update`, `delete`).
- If `method_config["resource"]` is truthy and a `repo` module path is provided, dynamically imports the repo class and instantiates it. The default routes are prepended to any existing `_routes` entries (so custom routes can override / extend behaviour).

### CRUD Endpoints
All endpoint methods expect to be mounted by `FastAPIWrapper` with dependency injection of JWT auth (`Depends(auth.get_auth)`), except `create` which is open by default (adjust YAML to secure it).

- `async create(self, data: dict) -> dict`
  - Validates incoming payload against `repo.schema_cls` (a Pydantic model).
  - On validation failure, returns HTTP 422 with field-level errors.
  - Calls `repo.create(data)` and wraps the result into `{"data": new_data}`.

- `async delete(self, id: str, token)`
  - Deletes the record via `repo.delete(id)` and returns `{"data": result}`.

- `async find(self, token)`
  - Retrieves all records via `repo.all()`, scrubs any `password` fields, and returns `{"data": result}`.

- `async findOne(self, id: str, token)`
  - Fetches a single record via `repo.one(id)`, removing `password` if present.

- `async update(self, id: str, data: dict, token)`
  - Delegates to `repo.update(id, data)` and returns `{"data": result}`.

When no repository is supplied, each method raises `NotImplementedError`, signalling that subclasses must override the behaviour.
