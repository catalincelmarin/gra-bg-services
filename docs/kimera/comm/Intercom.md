# Module `kimera.comm.Intercom`

Redis-backed pub/sub channel used for lightweight intra-service messaging.

## Data model
### `Message`
Pydantic model with validation rules:
- `type`: `"json"` or `"text"`.
- `content`: `dict` when `type="json"`, otherwise `str`.
- `channel`: Redis pub/sub channel name.

## `Intercom`
Singleton managing a shared Redis pubsub connection.

### Construction
`Intercom(redis_comm_url)` creates a Redis `PubSub`, stores the connection URL, and initialises a channel registry. Subsequent instantiations reuse the singleton.

### `async subscribe(self, channel, callback)`
Subscribes to a Redis channel and starts an async listener loop:
- Reads messages via `pubsub.get_message`.
- Decodes JSON payloads into `Message` objects.
- Passes the normalised `content` to the provided async `callback`.
- Runs as a background task using `asyncio.create_task`.

### `async publish(self, message: Message)`
Pushes the given message onto Redis by serialising the Pydantic model to JSON. Opens a transient connection for publishing to avoid blocking the shared pubsub connection.

### `async set/get/delete/exists`
Key-value convenience wrappers around Redis operations scoped to the global namespace (no namespacing beyond the caller-specified key).

### `emit(self, message: Message)`
Synchronous helper that spins up a new event loop, publishes via `publish`, and closes the loop—useful when called from synchronous code paths.
