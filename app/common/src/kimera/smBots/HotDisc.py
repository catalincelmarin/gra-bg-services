import discord
from discord.ext import commands


class HotDisc(commands.Bot):
    def __init__(self, token, command_prefix="/", **options):
        # Set up the bot with specified intents
        intents = discord.Intents.default()  # Start with the default intents
        intents.guilds = True  # Enable guild intents
        intents.messages = True  # Enable message intents
        intents.message_content = True  # Enable message content intents

        super().__init__(command_prefix=command_prefix, intents=intents, **options)
        self.token = token

    def register(self, with_class):
        use_bot = with_class(self)

        # Register commands
        for attr_name in dir(use_bot):
            if attr_name.startswith("cmd_"):
                cmd_name = attr_name[4:]  # Remove 'cmd_' prefix
                self.add_command_function(cmd_name, getattr(use_bot, attr_name))

        # Register events
        for attr_name in dir(use_bot):
            if attr_name.startswith("on_"):
                event_name = attr_name
                self.add_event_function(event_name, getattr(use_bot, attr_name))

    def run_bot(self):
        # Start the bot
        super().run(self.token)

    def add_command_function(self, name, callback):
        """Attach a command programmatically."""

        async def wrapped_callback(ctx, *args, **kwargs):
            return await callback(ctx, *args, **kwargs)
        self.command(name=name)(wrapped_callback)

    def add_event_function(self, event_name, callback):
        """Attach an event programmatically."""
        self.event(callback)
