# Module `kimera.db.BaseRepo`

Abstract contract for repositories backed by relational stores. Defines the CRUD surface that concrete repos must implement:
- `create(obj_data: dict) -> dict`
- `get(id) -> dict`
- `find(**filters) -> list[dict]`
- `update(id, obj_data) -> dict`
- `delete(id) -> bool`

Subclasses are expected to encapsulate persistence concerns and return serialisable representations (dicts) to higher layers.
