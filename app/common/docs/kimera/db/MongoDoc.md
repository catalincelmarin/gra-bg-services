# Module `kimera.db.MongoDoc`

Helpers that turn MongoEngine documents (and embedded structures) into plain Python dictionaries safe for JSON serialisation.

## `MongoDoc`

### `to_dict(object, exclude_fields=None)`
Accepts a document or list of documents. Delegates to `_mongo_to_dict` for single documents and applies it element-wise for lists. `exclude_fields` allows skipping attributes.

### `_mongo_to_dict(obj, exclude_fields)`
Internal walker that builds a list of key/value pairs:
- Skips excluded fields and the built-in Mongo-engine `id` alias (`_id` is converted separately).
- Handles field types:
  - `ListField`: processed via `list_field_to_dict`.
  - `EmbeddedDocumentField`: recursively processed.
  - `DictField`: copied as-is.
  - Scalar fields → normalised via `mongo_to_python_type`.
- Prepends `("id", str(obj.id))` when the input is a `Document`.

### `list_field_to_dict(list_field)`
Normalises each element to JSON-friendly values (recursing into embedded docs where necessary).

### `mongo_to_python_type(field, data)`
Maps MongoEngine field classes to Python primitives: `DateTimeField` → ISO string, `ObjectIdField` → str, etc. Unknown types fall back to `str(data)`.
