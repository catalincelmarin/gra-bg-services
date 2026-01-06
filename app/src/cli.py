"""Entry point for Kimera console launcher."""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Optional

import click
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from kimera.Bootstrap import Bootstrap, BootstrapException

console = Console()
_boot_instance: Optional[Bootstrap] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_config(yaml_file: Path) -> dict:
    """Safely load a YAML file and return an empty dict on failure."""
    try:
        with open(yaml_file, "r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}
    except FileNotFoundError:
        return {}


def get_class(class_path: str):
    """Import and return the class referenced by ``class_path``."""
    module = importlib.import_module(class_path)
    class_name = class_path.rsplit(".", 1)[-1]
    return getattr(module, class_name)


def _get_boot(silent: bool = False) -> Optional[Bootstrap]:
    """Lazily initialise Bootstrap so ``--help`` works without full boot."""
    global _boot_instance

    if _boot_instance is not None:
        return _boot_instance

    try:
        _boot_instance = Bootstrap()
    except BootstrapException as exc:
        if not silent:
            console.print(
                Panel.fit(
                    f"[red]Bootstrap failed:[/red] {exc}",
                    title="Kimera console",
                )
            )
        return None

    return _boot_instance


def _resolve_consoles_path() -> Path:
    boot = _get_boot(silent=True)
    if boot is not None:
        base_path = Path(boot.root_path)
    else:
        base_path = Path(__file__).resolve().parents[2]

    return (base_path / "app" / "config" / "consoles.yaml").resolve()


# ---------------------------------------------------------------------------
# Console launchers
# ---------------------------------------------------------------------------

def start_console(class_path: str) -> None:
    cli_class = get_class(class_path)

    @click.command(cls=cli_class)
    def cli() -> None:  # pragma: no cover - executed by click
        pass

    cli()


def start_c(console_name: str) -> None:
    config_path = _resolve_consoles_path()
    config = load_config(config_path)
    consoles = config.get("consoles", [])

    console_entry = next((c for c in consoles if c.get("name") == console_name), None)

    if not console_entry:
        console.print(f"[red]Console '{console_name}' not found in {config_path}[/red]")
        sys.exit(1)

    _get_boot()  # ensure bootstrap inits for real run
    start_console(console_entry["classPath"])


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def start() -> None:
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help") or args[0].startswith("-"):
        display_help()
        sys.exit(0)

    use_console = args[0]
    # Remove the console argument so downstream click sees only console args
    sys.argv.pop(1)
    start_c(use_console)


def display_help() -> None:
    config_path = _resolve_consoles_path()
    config = load_config(config_path)
    consoles = config.get("consoles", [])

    console.print(
        Panel.fit(
            "[bold magenta]Kimera console running...[/bold magenta]",
            title="Kimera",
            subtitle="Command Gateway",
        )
    )

    if not consoles:
        console.print(
            Panel.fit(
                f"[yellow]No consoles declared in[/yellow]\n[white]{config_path}[/white]",
                title="Configuration",
            )
        )
        console.print("Usage: [bold]./cli <console_name> [options][/bold]")
        return

    table = Table(show_header=True, header_style="bold cyan", title="Available Consoles")
    table.add_column("Name", style="green", no_wrap=True)
    table.add_column("Class Path", style="white")

    for entry in consoles:
        name = str(entry.get("name", "-"))
        class_path = str(entry.get("classPath", "-"))
        table.add_row(name, class_path)

    console.print(table)
    console.print("Usage: [bold]./cli <console_name> [options][/bold]")


if __name__ == "__main__":  # pragma: no cover
    start()
