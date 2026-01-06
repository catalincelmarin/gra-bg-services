# Module `kimera.comm.PubSub`

Kafka integration layer that encapsulates publisher/subscriber setup, message serialisation, and topic management.

## Enums
- `KafkaContentTypes`: currently `APPLICATION_JSON` and `TEXT_PLAIN`.

## Publishing
### `Pub`
- Constructor: `Pub(kafka_servers, topic, contentType=KafkaContentTypes.APPLICATION_JSON)` prepares a Kafka `Producer` and stores the desired content type.
- `topicExists() -> bool`: Uses `AdminClient` to check whether the topic already exists.
- `_create_topic_if_not_exists()`: Creates the topic with partitions=1, replication factor=1 if missing.
- `publish(message=None, callback=None)`: Serialises `message` via `DataMapper.json`, attaches content-type headers, and sends it. If `callback` is provided, it's passed to Kafka's produce call.

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
