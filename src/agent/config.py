import os
import tomllib
from pathlib import Path
from typing import Literal

# create a folder to store the generated code
SUPPORTED_LANGUAGES = ["python", "typescript", "javascript"]
SUPPORTED_FRAMEWORKS = ["playwright", "cypress"]


def get_test_dir() -> Path:
    x: Literal["cypress", "playwright", "out"] = os.environ.get(
        "AGENT_FRAMEWORK", "playwright"
    )
    test_dir = Path(x) if x else Path("out")
    test_dir.mkdir(exist_ok=True)
    return test_dir


def read_config():
    config_file = Path("config.toml")

    if config_file.exists():
        with open(config_file, "rb") as f:
            config = tomllib.load(f)

    return config
