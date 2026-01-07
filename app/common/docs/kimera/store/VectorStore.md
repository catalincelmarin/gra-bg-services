# Module `kimera.store.VectorStore`

Minimal vector-store wrapper around MongoDB collections for embedding persistence.

## `VectorRepo`
Internal helper class:
- Constructor binds a `Store` and target collection.
- `save(text, vector)`: Stores the document with vector converted to a list.
- `load()`: Returns a cursor of `{text, vector}` documents.
- `clear()`: Deletes all documents.
- `drop()`: Drops the collection entirely.

## `VectorStore`

### Constructor
`VectorStore(store, collection_name, **kwargs)` initialises a `VectorRepo` and captures optional metadata:
- `embedder`: identifier of the embedding backend.
- `model`: embedding model name.
- `dimension`: expected vector size (coerced to `int` when possible).
- Extra `kwargs` are stored verbatim.

### Persistence API
- `add_vector(text, vector)`: Accepts `numpy.ndarray` or list of floats and saves the pair.
- `load()`: Returns the repo cursor for downstream similarity search.
- `clear()`: Empties the collection.
- `drop()`: Drops the collection.
- `clone_store(target_name, copy_indexes=True)`: Uses MongoDB's `$out` aggregation to clone all documents into a new collection and optionally replicates indexes. Returns a new `VectorStore` bound to the target.

### Metadata accessors
- `embedder`
- `model`
- `dimension`
- `kwargs`: returns a shallow copy of the original kwargs.
