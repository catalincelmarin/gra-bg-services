# Module `kimera.smBots.HotDisc`

Discord bot harness built on `discord.ext.commands.Bot`.

## `HotDisc`
Subclass of `commands.Bot` that preconfigures intents and adds dynamic registration helpers.

### Constructor
`HotDisc(token: str, command_prefix="/", **options)`:
- Enables default intents plus `guilds`, `messages`, and `message_content`.
- Stores the provided bot `token` for later use with `run_bot`.

### `register(self, with_class)`
Instantiates `with_class(self)` and inspects it for hook methods:
- Any attribute named `cmd_<name>` is registered as a command named `<name>`.
- Any attribute starting with `on_` is registered as an event handler.

### `run_bot(self) -> None`
Invokes the parent `run(token)` method to start the bot.

### `add_command_function(self, name, callback)`
Decorator helper used internally by `register`. Wraps `callback` into an async command coroutine and attaches it to the bot at runtime.

### `add_event_function(self, event_name, callback)`
Registers a coroutine as an event listener (e.g., `on_message`).
