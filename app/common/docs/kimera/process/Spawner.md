# Module `kimera.process.Spawner`

Singleton that spawns long-running coroutines as OS processes or threads, while keeping graceful-stop signals.

## `Spawner`

### Construction
`Spawner()` returns the shared instance. The first construction initialises registries:
- `processes`: name → `multiprocessing.Process`
- `threads`: name → `threading.Thread`
- `kill_threads`: reserved dict (currently unused)
- `shutdown_signals`: name → `threading.Event` or `multiprocessing.Event`

### `thread_loop(self, name, coro, params=None, perpetual=True)`
Launches an async coroutine in a dedicated **thread**.
- `name`: logical name; actual thread name becomes `thread-{name}`.
- `coro`: async function to execute.
- `params`: dict bound as keyword arguments.
- `perpetual=True`: run forever by creating a new event loop and repeatedly awaiting the coroutine until `shutdown_signals[name]` is set. When `False`, the coroutine is run to completion once.
Returns the `threading.Thread` when `perpetual` is truthy; otherwise `None`.

### `loop(self, name, coro, params=None, perpetual=True)`
Starts an async coroutine in a separate **process**.
- Creates a fresh event loop in the child process.
- When `perpetual` is `True`, keeps the coroutine alive until the multiprocessing `Event` (`shutdown_signals[name]`) is set.
- When `False`, runs `coro(**params)` once and exits.
- Returns the new process PID or `None` on failure.

### `_graceful_task_wrapper(self, coro, params, stop_event)`
Internal awaitable that re-dispatches `coro(**params)` and sleeps 100 ms between checks until `stop_event` is set, then cancels the task for a clean shutdown.

### `start(self, name, target, daemon=True, *args)`
Runs an arbitrary callable in a new process and tracks it.
- Wraps `target(*args, stop_event)` in a `multiprocessing.Process`.
- Stores the accompanying `stop_event` in `shutdown_signals`.
- Returns the child PID if available.

### `stop(self, name) -> bool`
Signals a named thread/process to stop and, if necessary, escalates to `os.kill(..., SIGKILL)` after a 3-second timeout. Cleans up registry entries and returns `True` when the process is no longer alive.

### `restart(self, name, target, *args)`
Calls `stop(name)` followed by `start(name, target, *args)`.

### `monitor(self)`
Iterates tracked processes and restarts any that have died, reusing the original target/arguments (minus the internally appended stop event).

### `ps(self)`
Prints the status of each registered process.

### `cleanup(self)`
Stops all tracked processes by delegating to `stop(name)` for each entry.
