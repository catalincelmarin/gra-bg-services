# Module `kimera.comm.PubSub`

Kafka integration layer that encapsulates publisher/subscriber setup, message serialisation, and topic management.

## Enums
- `KafkaContentTypes`: currently `APPLICATION_JSON` and `TEXT_PLAIN`.

## Publishing
### `Pub`
- Constructor: `Pub(kafka_servers, topic, contentType=KafkaContentTypes.APPLICATION_JSON, ack_handler: Callable[[dict], Awaitable[None]] | None = None)` prepares a Kafka `Producer`, stores the desired content type, and optionally binds an async ack handler.
- `topicExists() -> bool`: Uses `AdminClient` to check whether the topic already exists.
- `_create_topic_if_not_exists()`: Creates the topic with partitions=1, replication factor=1 if missing.
- `publish(message=None, callback=None)`: Serialises `message` via `DataMapper.json({"data": message})`, attaches content-type headers, and sends it. If `callback` is provided, it is invoked alongside the optional ack handler.

### `PubFactory`
Registry that caches publishers by name.
- `set(kafka_servers, name, topic, contentType)`
- `get(name) -> Pub`
- `all()` returns the registry dict.
- `publish(to, message)` convenience wrapper around `get(...).publish(...)`.

## Subscription
### `Sub`
- Constructor: `Sub(kafka_servers, group_id, topic, name, handler, contentType=KafkaContentTypes.APPLICATION_JSON)` sets up a Kafka `Consumer` and remembers the async `handler`.
- `topicExists()`: Same metadata lookup as in `Pub`.
- `async _run(self)`: Waits for the topic to appear, subscribes, and polls for messages. Each message is decoded according to its headers; JSON payloads are deserialised and passed to `handler(data=...)` via `asyncio.gather`.
- `listen(...)`: Starts a dedicated event loop and runs `_run()` until exception or interrupt.

`Helpers.sysPrint` is used liberally for visibility (e.g., when waiting for topics).

## Ack handlers (Publishers)
Publishers can optionally bind an async acknowledgment handler that is invoked when Kafka delivers (or fails to deliver) a message. When configured, delivery reports are normalised into a dict and dispatched on a background asyncio loop so they never block Kafka's delivery thread.

- Constructor support: `Pub(..., ack_handler: Callable[[dict], Awaitable[None]] | None = None)`.
- Handler signature: `async def on_published(event: dict) -> None`.
- Payload schema:
  - `status`: `"ok"` or `"error"`
  - `error`: `None` on success, else `{ "message": str, "code": str | None }`
  - `meta`: `{ topic, partition, offset, timestamp, key, headers, contentType }`
  - `data`: normalized content (parsed JSON dict when contentType is `application/json`; otherwise `{ "text": "..." }`)
- Delivery callbacks always schedule the handler on the publisher's private asyncio loop. Handler exceptions are caught and logged.

### Config wiring
In `app/config/kafka.yaml`, a publisher can specify an optional `ackHandler` dotted path, resolved during bootstrap:

```yaml
pubs:
  - name: myPub
    topic: orders.v1
    server: KAFKA_BOOTSTRAP
    contentType: application/json
    ackHandler: myapp.handlers.PublishAcks.on_published
```

This is resolved by `Bootstrap._get_method_ref` and passed to `PubFactory.set(..., ack_handler=...)`.
