# Module `kimera.helpers.DataMapper`

Utilities that translate between Python data structures, MongoDB/BSON types, Pandas DataFrames, and JSON.

## `DataMapper`
Static helper namespace.

### `df_to_xlsx(dataframe, file_path, include_headers=True) -> bool`
Writes a Pandas DataFrame to an Excel workbook using `DataFrame.to_excel`. Returns `True` on success, `False` on any exception (the caller can log the failure). `include_headers` controls whether column headers are emitted.

### `transform_document(example_document: dict, mapper: dict) -> dict`
Deep-maps `example_document` into a new dict using a mapping specification:
- `_transform`: optional callable applied to the source value before copying.
- `_to`: target key name. Absent means keep the original key.
- `_sub`: nested mapping for dict-valued children.
- `_push`: when provided, pushes the transformed child into a list stored under `_push` and removes the direct field.
Keys that are not described in `mapper` are copied verbatim.

### `to_dict(doc: dict | list) -> dict | list`
Recursively normalises MongoEngine/MongoDB documents:
- Converts `Decimal128`, `datetime`, `ObjectId` to JSON-friendly primitives.
- Strips `_id` and reassigns it to `id` for top-level documents.
- Works on nested dicts and lists in-place (a defensive copy is expected upstream).

### `json(obj: Any) -> str`
Serialises any object after passing it through `to_dict`, ensuring BSON types are safe for JSON encoding.

### `from_json(obj: dict | list) -> dict | list`
Reverse operation that attempts to rehydrate ISO8601 strings into `datetime` objects while descending through dicts/lists. Strings that fail `datetime.fromisoformat` remain untouched.
