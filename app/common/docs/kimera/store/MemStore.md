# Module `kimera.store.MemStore`

Redis-backed key/value store with optional hash operations and pickle-based value serialisation.

## `MemStore(uri, connection_name='default', namespace='_root')`
- `uri`: Redis connection string.
- `namespace`: Prefixed to every key (`namespace:key`).
- Serialises values by `pickle.dumps` + base64 encoding to maintain type fidelity.

### Basic operations
- `_full_key(key)`: Internal helper for namespacing.
- `set(key, value)`: Stores any pickle-able value; logs when `DEBUG_STORES` is set.
- `get(key, default=None)`: Retrieves and decodes the value, returning `default` if missing or decoding fails.
- `delete(key)`: Removes the key.
- `keys(pattern='*')`: Lists all keys under the namespace matching the pattern.
- `flush()`: Deletes every key in the namespace.
- `close()`: Closes the Redis connection.

### Hash operations
For high-frequency use cases, exposes direct Redis hash commands:
- `hset(key, field=None, value=None, mapping=None)`
- `hget(key, field)`
- `hgetall(key)`
- `hdel(key, field)`

All methods catch and log exceptions using `Helpers.errPrint`.
