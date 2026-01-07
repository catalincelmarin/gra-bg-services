# Module `kimera.store.BaseDocument`

Abstract MongoEngine document that standardises JSON serialisation.

## `BaseDocument(Document)`
- Declares `meta = {'abstract': True}` so it can be inherited without creating its own collection.
- `__private__`: list of fields to exclude from the output.
- `__expand__`: list of reference field names that should be expanded into nested dicts rather than string IDs.

### `to_dict(self) -> dict`
- Converts the document to a dict via `to_mongo().to_dict()`.
- Moves `_id` to `id` (stringified).
- For each attribute:
  - Skips fields listed in `__private__`.
  - Reference fields: include expanded dicts when the field is listed in `__expand__`; otherwise serialise as string IDs.
  - `ListField` of references: optionally expand each reference if listed in `__expand__`.

Resulting dict is safe for JSON serialisation and respects privacy/expansion hints defined on subclasses.
