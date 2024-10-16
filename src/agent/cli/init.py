import typer
from typing_extensions import Annotated
from typing import Optional
from pathlib import Path
from agent.setup import TEST_DIR


def init(
    folder: Annotated[
        Optional[Path],
        typer.Argument(help="The folder to initialise the project in."),
    ] = ".",
):
    """Initialise a new directory for the project 🚀"""
    # make the project directory if it doesn't exist
    folder.mkdir(exist_ok=True)

    # create the tests folder if it doesn't exist
    test_dir = folder / TEST_DIR
    test_dir.mkdir(exist_ok=True)

    # create an .env file if it doesn't exist
    env_dir = folder / ".env"
    if not (env_dir).exists():
        with open(env_dir, "w") as f:
            f.write("OPENAI_API_KEY=''\n")
            f.write("OPENAI_MODEL='gpt-4o'\n")
            f.write("HEADLESS=true\n")
            f.write("LOG_LEVEL=INFO\n")

    # create a .gitignore file if it doesn't exist
    gitignore_dir = folder / ".gitignore"
    if not (gitignore_dir).exists():
        with open(gitignore_dir, "w") as f:
            f.write(".env\n")

    # create a config.toml file if it doesn't exist
    agent_config_dir = folder / "config.toml"
    if not (agent_config_dir).exists():
        with open(agent_config_dir, "w") as f:
            f.write("[agent]\n")
            f.write(
                'prompt = "Write some playwright tests in python for the signup flow"\n'
            )
            f.write('url = "https://dev.datamaker.app"\n')
