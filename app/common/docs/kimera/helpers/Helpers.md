# Module `kimera.helpers.Helpers`

ANSI-aware console helpers used across Kimera services for consistent, colored output.

## `bcolors`
Container for escape sequences used to style terminal output. All attributes are upper-case strings such as `HEADER`, `OKBLUE`, `WARNING`, etc. Used internally by `Helpers`.

## `Helpers`
Namespace of static helpers; instantiate is unnecessary.

### `print(*arguments) -> None`
Pretty-prints any mix of primitives or mappings:
- Strings are tokenised on spaces so numeric components can be highlighted in yellow.
- Integers/floats are rendered in yellow (via `bcolors.WARNING`).
- For mappings, `_id` keys are stripped, `datetime` and `time` objects get ISO-like formatting, then the structure is syntax-highlighted using `pygments`' JSON lexer and emitted with ANSI colours.
- Non-dict iterables fall back to `repr()`.

### `sysPrint(subject, info="") -> None`
Convenience wrapper that prints a blue, bold subject with an optional green payload (prepends `INITIALIZING : FULL`, etc.). Used for phase banners.

### `errPrint(message, file="", line=0) -> None`
Formats an error header in red/bold and appends the `message`. Designed for quick inline exception reporting where structured logging is unavailable.

### `warnPrint(message) -> None`
Yellow "WARN" banner plus the supplied message.

### `tracePrint(exc, message="", **kwargs) -> None`
Fully formatted exception trace:
- Shows an optional `message` banner.
- Prints `TypeErrorName: message` in red.
- Iterates over `traceback.format_exception` output and colourises each line yellow.

### `infoPrint(message) -> None`
Cyan "INFO" banner for informational messages.

### `sigPrint(message) -> None`
Cyan "SIGNAL" banner. Used when broadcasting pub/sub style state changes.
