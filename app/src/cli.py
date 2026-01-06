import yaml
import click
import importlib
import sys
from kimera.Bootstrap import Bootstrap

boot = Bootstrap()


# Load YAML config
def load_config(yaml_file):
    with open(yaml_file, "r") as file:
        return yaml.safe_load(file)


# Dynamically import class from path
def get_class(class_path, name):
    module_name, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_name + "." + name)
    return getattr(module, class_name)


def start_console(class_path):
    name = class_path.split(".")[-1]
    cli_class = get_class(class_path,name)

    @click.command(cls=cli_class)
    def cli():
        pass

    cli()


def start_c(console_name):
    config = load_config(f"{boot.root_path}/app/config/consoles.yaml")  # Ensure the correct path
    consoles = config.get("consoles", [])

    console_entry = next((c for c in consoles if c["name"] == console_name), None)

    if not console_entry:
        print(f"Error: Console '{console_name}' not found in consoles.yaml")
        sys.exit(1)

    start_console(console_entry["classPath"])

def start():
    if len(sys.argv) < 2:
        print("Usage: ./cli <console_name>")
        sys.exit(1)
    use_console = sys.argv[1]
    sys.argv.pop(1)
    start_c(use_console)



