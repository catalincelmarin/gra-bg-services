# Module `kimera.dev.Loggers`

Configures named `logging.Logger` instances backed by rotating file handlers under `/home/jazzms/app/logs/` and a shared stderr stream handler. The active level defaults to `INFO` and can be overridden via the `LOGGER_LEVEL` environment variable.

Each class is a simple namespace that exposes a class-level `logger` configured at import time:

- `APILogger`
- `KafkaLogger`
- `GPTLogger`
- `ConsoleLogger`
- `TaskLogger`

Every logger writes to a dedicated log file (e.g., `api.log`, `kafka.log`, etc.) and mirrors output to stderr.

`GPTLogger` creates its own stream handler instance to avoid sharing references.

At module import the process' stdout is reset to the original system stdout (`sys.__stdout__`).
