# Module `kimera.process.TaskManager`

Celery orchestration utilities for dispatching distributed jobs and composing them into higher-level workflows.

## Exceptions
- `TimeoutException`: Raised when `send_await` exceeds the configured timeout.

## `TaskParams`
Validated container that describes a Celery task invocation.
- Validates inputs using an inner Pydantic model at construction time.
- Attributes:
  - `friend`: logical friend name (must exist in Celery friends config).
  - `task_name`: function registered on the friend.
  - `callback`: optional async function executed when `send_async` completes.
  - `args`: positional argument list (defaults to `[]`).
  - `kwargs`: keyword argument dict (defaults to `{}`).
  - `timeout`: seconds to wait before treating the task as failed.

## `TaskManager`
Singleton that lazily loads Celery configuration from `Bootstrap`.

### Construction
- The first `TaskManager()` call loads `.env`, instantiates `Bootstrap()`, and reads `celery_broker`, `celery_backend`, and friend definitions.
- If `Bootstrap` reports `celery_on=False`, Celery calls raise exceptions.

### Properties
- `celery_app`: underlying Celery application or `None` when Celery is disabled.
- `friends`: dict mapping friend names to configuration payloads from `friends.yaml`.

### `send_async(...) -> asyncio.Task`
Fires a task via `celery_app.send_task` and polls for completion with exponential backoff between `poll_start` and `max_poll` seconds. Once successful:
- `callback` (async) is awaited if provided.
- `func` (sync) is called if provided.
- The Celery `AsyncResult` is forgotten and revoked to release broker resources.
Returns a background asyncio Task for the polling coroutine.

### `send_await(...) -> Any`
Same dispatch mechanism as `send_async` but awaits the result inline. Raises `TimeoutException` if an `asyncio.wait_for` boundary (default `timeout=30`) is exceeded.

### `paraSyncTasks(taskList)`
Concurrently await multiple `TaskParams` using `send_await`. Returns a list of results (or exceptions) once all complete.

### `paraTasks(taskList, gather_callback=None)`
Fire-and-forget version that wraps each `TaskParams` in `send_async`. If `gather_callback` is a coroutine, schedules it once all tasks resolve; otherwise returns the awaited aggregate result list.

### `chainSyncTasks(taskList)`
Sequentially executes tasks, feeding each result into the next task's kwargs/args (`dict` → `kwargs`, `list` → `args`, scalar → `payload`). Logs each intermediate result via `Helpers.sysPrint` and returns the final payload.

### `chainTasks(taskList)`
Asynchronous chain runner that wires callbacks to propagate results between tasks without blocking the event loop. Returns the initial `send_async` task handle.

### `_get_callback_wrapper(self)`
Factory that builds the recursive callback used by `chainTasks` to funnel results through the sequence.
