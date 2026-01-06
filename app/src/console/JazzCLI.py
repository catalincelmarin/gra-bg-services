from pathlib import Path

import click
import yaml
from kimera.Bootstrap import Bootstrap
from passlib.hash import bcrypt
from rich.console import Console

from app.src.data.nosql.repo.Assistants import Assistants
from app.src.data.nosql.repo.Users import Users
from app.src.data.nosql.schemas.Assistant import Assistant

console = Console()
class JazzCLI(click.MultiCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def list_commands(self, ctx):
        # Return the available commands in the CLI
        return ['create-user','sync-bots']

    def get_command(self, ctx, name):
        if name == 'create-user':
            return self.create_user
        # Register the command based on the name
        if name == 'sync-bots':
            return self.sync_bots




    @staticmethod
    @click.command(help="synchronize bots from yamls to db")
    @click.option('-bot', type=str, help="Bot name (camel cased start with capital)")
    def sync_bots(bot: str):
        boot = Bootstrap()
        ext_path = f"{boot.root_path}/app/ext"

        # Use pathlib for cleaner code to find bot files
        bot_files = list(Path(ext_path).rglob(f"bot.{bot}.yaml"))

        # Check if the specific bot file exists
        if bot_files:
            # If the bot file is found, load it safely (assuming YAML format)
            bot_file = bot_files[0]  # There should only be one result due to the filename pattern
            print(f"Found bot file: {bot_file}")
            with open(bot_file, 'r') as file:
                try:
                    bot_data = yaml.safe_load(file)  # Safely load the YAML file
                    setup = bot_data.get("setup")
                    new_bot = Assistant(
                        name=setup.get("name"),
                        bot_path=setup.get("module"),
                        bot=setup.get("bot"),
                        description=setup.get("description"),
                        api_converse=setup.get("api_converse")
                    )
                    exists = Assistants().getOne(name=setup.get("name"))
                    if exists:
                        exists.bot_path = new_bot.bot_path
                        exists.bot = new_bot.bot
                        exists.description = new_bot.description
                        exists.api_converse = new_bot.api_converse
                        exists.save()
                    else:
                        new_bot.save()
                    click.secho(f"Bot saved", fg="green")
                except yaml.YAMLError as e:
                    print(f"Error loading YAML file: {e}")
        else:
            # If the bot file does not exist, print a colored message using Click
            click.secho(f"Bot file 'bot.{bot}.yaml' does not exist in ext.", fg="red")

    @staticmethod
    @click.command(help="Create a new user in the system with a wizard-like interface.")
    def create_user():
        """ Command to guide through a wizard for creating a new user. """

        # Step 1: Ask for the username
        username = click.prompt("Step 1: Enter a unique username")
        if not username:
            console.print("[bold red]Username cannot be empty![/bold red]")
            return

        # Step 2: Ask for the full name
        name = click.prompt("Step 2: Enter the full name of the user", default="")

        # Step 3: Ask for the email and validate format
        while True:
            email = click.prompt("Step 3: Enter the user's email")
            if "@" not in email or "." not in email:
                console.print("[bold red]Invalid email format. Please try again.[/bold red]")
            else:
                break

        # Step 4: Ask for password and confirm it
        while True:
            password = click.prompt("Step 4: Enter a password", hide_input=True, confirmation_prompt=True)
            if len(password) < 5:
                console.print("[bold red]Password must be at least 5 characters long![/bold red]")
            else:
                break

        # Step 5: Ask for the role
        role = click.prompt("Step 5: Enter the user's role (e.g., 22222 for admin, user)", default="user")

        # Step 6: Ask for GitHub credentials
        github = click.prompt("Step 6: Enter GitHub credentials (username:token)", default="")

        # Step 7: Ask for API keys (optional)
        api_keys = click.prompt("Step 7: Enter comma-separated API keys (optional)", default="")
        api_keys_list = [key.strip() for key in api_keys.split(",") if key.strip()]

        # Confirm user information before creating
        console.print("\n[bold cyan]Summary of entered details:[/bold cyan]")
        console.print(f"Username: [bold green]{username}[/bold green]")
        console.print(f"Name: [bold green]{name}[/bold green]")
        console.print(f"Email: [bold green]{email}[/bold green]")
        console.print(f"Role: [bold green]{role}[/bold green]")
        console.print(f"GitHub: [bold green]{github}[/bold green]")
        console.print(f"API Keys: [bold green]{api_keys_list}[/bold green]")

        if not click.confirm("Do you want to create this user with the above information?", default=True):
            console.print("[bold red]User creation canceled.[/bold red]")
            return

        # Hash the password before saving


        # Prepare the user data
        user_data = {
            "username": username,
            "name": name,
            "email": email,
            "password": password,
            "role": role,
            "github": github,
            "api_keys": api_keys_list
        }

        # Create the user via the Users repository
        users_repo = Users()
        try:
            user_id = users_repo.create(user_data)
            console.print(f"[bold green]User created successfully with ID: {user_id}[/bold green]")
        except Exception as e:
            console.print(f"[bold red]Error creating user: {e}[/bold red]")

