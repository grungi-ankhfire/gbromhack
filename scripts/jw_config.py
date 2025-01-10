import tomllib
from pathlib import Path

CONFIG_FOLDER = Path(__file__).parent

# config = configparser.ConfigParser()
# config.read(CONFIG_FOLDER / 'config.ini')
config = None
with open(CONFIG_FOLDER / 'config.toml', "rb") as f:
    config = tomllib.load(f)
