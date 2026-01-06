# Module `kimera.store.StoreFactory`

Central registry that lazily instantiates and caches various store implementations based on configuration files.

## Supporting types
- `MemConnection`: Pydantic model holding a Redis URI and a namespace→`MemStore` mapping.
- `StoreNotFound`: Custom exception raised when requesting a Redis namespace without a known connection URI.

## Store registries
- `_store_instances`: Mongo stores (`Store`).
- `_es_store_instances`: Elasticsearch connections.
- `_file_store_instances`: File-system stores.
- `_mem_store_instances`: `MemConnection` objects keyed by Redis connection name.
- `_vector_store_instances`: Vector stores backed by Mongo collections.
- `_rdb_store_instances`: Relational stores (`Database`).

## Factory methods
- `get_store(connection_name, uri=None, **kwargs)` → `Store`
- `get_es_store(connection_name, uri=None, index=None, **kwargs)` → `ElasticStore`
- `get_vector_store(connection_name, collection=None, uri=None, **kwargs)` → `VectorStore`
  - When a store already exists, calling with a new `collection` clones the underlying repo to a new key `<connection_name>_<collection>`.
- `get_mem_store(namespace="_root", connection_name="default", uri=None, **kwargs)` → `MemStore`
  - Creates a `MemConnection` when first called with a URI, then lazily initialises per-namespace `MemStore` instances.
- `get_fstore(store_name, path=None, **kwargs)` → `LocalFileStore`
- `get_rdb_store(connection_name, uri=None, **kwargs)` → `Database`

## `load_stores(stores_path: str)`
Walks `<stores_path>/app/**/stores.*.yaml`, reads `stores:` definitions, resolves URIs from environment variables, and initialises the appropriate store type using the factory methods. Tracks total/loaded/failed counts and logs failures via `Helpers.tracePrint`.
