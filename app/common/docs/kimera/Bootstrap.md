# Module `kimera.Bootstrap`

Bootstraps a Kimera service: loading environment settings, wiring Kafka, Celery, stores, Intercom, and the HTTP API.

## `BootstrapException`
Custom exception used when the bootstrap sequence cannot proceed.

- `__str__(self) -> str`: Returns a prefixed version of the message for logging.
- `log_error(self) -> None`: Convenience helper that prints an `ERROR:` line. Used where raising is not desirable.

## `Bootstrap`
Singleton responsible for initializing cross-cutting services. Access it via `Bootstrap()`; the first call expects the `APP_PATH` environment variable to be set.

### Lifecycle
- `__new__(cls, full: bool = False)`: Enforces singleton semantics and checks `APP_PATH`. The first instantiation immediately calls `_initialize()`.
- `_initialize(self, app_path: str, full: bool = False)`: Orchestrates the boot steps. Loads environment flags, starts Intercom, optionally Kafka, always stores and Celery, and finally the HTTP API using `JWTAuth` by default. When `full=True`, prints status banners via `Helpers.sysPrint`.

### Helpers
- `_get_method_ref(full_path: str) -> Callable`: Resolves a dotted path like `pkg.module.Class.method` to a callable. Used for Kafka subscriber handlers.
- `_load_environment(self) -> None`: Consumes `.env` via `load_dotenv()`, caches feature toggles (`API`, `KAFKA`, `CELERY`) and `EXTERNAL_PORT` onto the instance.
- `_load_friends_config(path: str) -> dict`: YAML loader for Celery "friends" configuration. Missing files return `{}`.
- `_load_kafka_config(path: str) -> dict`: YAML loader for Kafka wiring. Missing files return `{}`.

### API orchestration
- `start_api(self, auth: BaseAuth | None = None) -> None`: Spins up the FastAPI/Socket.IO stack through `FastAPIWrapper.runApi`. No-op when `API` flag is false.
- `api(self) -> FastAPIWrapper | None`: Property exposing the wrapper that hosts the FastAPI app and Socket.IO server.
- `root_path(self) -> str`: Property exposing the resolved application root used for configuration discovery.

### Intercom
- `_setup_intercom(self) -> None`: Instantiates the Redis-backed `Intercom`. Uses `REDIS_COMM` from the environment.
- `run_intercom(self, channel: str, callback: Callable) -> Awaitable[None]`: Subscribes to an Intercom channel; prints status banners when booted in `full` mode.

### Kafka
- `_setup_kafka(self, full: bool = False) -> None`: Loads Kafka publishers and subscribers from `config/kafka.yaml`. Registers publishers through `PubFactory.set` and hands subscribers to `ThreadKraken` for concurrent listening. Validates handler dotted paths and environment-provided broker URLs; raises `KafkaException` when misconfigured.

### Celery
- `_setup_celery(self, celeryconfig=None) -> None`: Caches Celery configuration when `CELERY=1`. Reads broker/backend URLs from environment, stores friend definitions via `_load_celery_friends()`.
- `_load_celery_friends(self) -> dict`: Reads `config/friends.yaml` and returns the `friends:` mapping, or `{}` if the file is absent.

### Stores
- `_setup_stores(self) -> None`: Delegates to `StoreFactory.load_stores` to register Mongo/SQL/Redis/etc. stores declared under the app.

### Flags & API bootstrap
- `_load_environment()` populates `api_on`, `kafka_on`, `celery_on`, and `EXTERNAL_PORT`. Those flags govern whether `_setup_kafka`, `_setup_celery`, and `start_api` execute.

### Error handling
Most helper methods raise `BootstrapException` for environment mistakes (e.g., missing `APP_PATH`) or propagate upstream exceptions (Kafka misconfiguration, YAML errors) so the caller can decide whether to abort startup.
