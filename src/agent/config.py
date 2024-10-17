import tomllib
from pathlib import Path

# create a folder to store the generated code
TEST_DIR = Path("tests")


def read_config():
    config_file = Path("config.toml")

    if config_file.exists():
        with open(config_file, "rb") as f:
            config = tomllib.load(f)

    return config
