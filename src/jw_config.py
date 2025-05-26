import tomllib
from pathlib import Path

# Looking for a config file at the project root
CONFIG_FOLDER = Path(__file__).parent.parent

config = None
with open(CONFIG_FOLDER / 'config.toml', "rb") as f:
    config = tomllib.load(f)


def path(relative_path: str|Path) -> Path:
    return CONFIG_FOLDER / relative_path




