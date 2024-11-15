import typer
from typing_extensions import Annotated
from typing import Optional
from pathlib import Path
from agent.config import get_test_dir
from agent.logging import console
from rich.panel import Panel
from rich.markdown import Markdown


def init(
    folder: Annotated[
        Optional[Path],
        typer.Argument(help="The folder to initialise the project in."),
    ] = ".",
):
    """Initialise a new directory for the project 🚀"""

    if str(folder) == ".":
        # ask for confirmation
        confirm = typer.confirm(
            "Do you want to initialise the project in the current directory?"
        )
        if not confirm:
            raise typer.Exit()

    # make the project directory if it doesn't exist
    folder.mkdir(exist_ok=True)

    # create the tests folder if it doesn't exist
    test_dir = get_test_dir()
    test_dir = folder / test_dir
    test_dir.mkdir(exist_ok=True)

    # create an .env file if it doesn't exist
    env_dir = folder / ".env"
    if not (env_dir).exists():
        with open(env_dir, "w") as f:
            f.write("OPENAI_API_KEY=''\n")

    # create a .gitignore file if it doesn't exist
    gitignore_dir = folder / ".gitignore"
    if not (gitignore_dir).exists():
        with open(gitignore_dir, "w") as f:
            f.write(".env\n")

    # create a config.toml file if it doesn't exist
    agent_config_dir = folder / "config.toml"
    if not (agent_config_dir).exists():
        with open(agent_config_dir, "w") as f:
            config_toml = r"""
[config]
language = "python"
framework = "playwright"
headless = false
clean = true
log_level = "INFO"

[agent]
url = "https://dev.datamaker.app"
prompt = '''
Test the signup and sign in flow of the app
'''
"""
            f.write(config_toml)
    console.print("\n")
    console.print(
        Panel(
            Markdown(
                f"""
You can start writing tests using the agent CLI. Run the following commands to get started:
- cd {folder}
- agent start

You may also need to add your *OPENAI_API_KEY* to the **.env** file. Modify your *prompt* in the **config.toml** file
"""
            ),
            padding=(1, 1),
            title="New project initialised successfully! 🚀",
            highlight=True,
            title_align="left",
        )
    )
    console.print("\n")
