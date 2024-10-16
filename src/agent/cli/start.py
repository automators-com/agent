import typer
import tomllib
from pathlib import Path
from typing import Optional
from typing_extensions import Annotated
from agent.setup import clean_dir
from agent.completions import agent
from agent.logging import logger

from rich.console import Console

err_console = Console(stderr=True)


def start(
    prompt: Annotated[
        str,
        typer.Option(help="A prompt describing the scope of your tests."),
    ] = None,
    url: Annotated[
        str,
        typer.Option(help="A url that acts as an entrypoint to app you're testing."),
    ] = None,
    clean: Annotated[
        bool,
        typer.Option(
            help="Delete files from the 'tests' directory before starting the agent."
        ),
    ] = False,
):
    """Starts the test generation agent ✨"""

    if not prompt or not url:
        # check if the config file exists
        config_file = Path("config.toml")

        if config_file.exists():
            logger.info("Reading configuration from [purple3]config.toml[/purple3]")

            with open(config_file, "rb") as f:
                config = tomllib.load(f)

            prompt = config.get("agent", {}).get("prompt") or config.get("prompt")
            url = config.get("agent", {}).get("url") or config.get("url")

        else:
            err_console.print(
                "Please pass a [purple3]--prompt[/purple3] and [purple3]--url[/purple3] when starting the agent. Alternatively, create a [purple3]config.toml[/purple3] file with the required fields."
            )
            raise typer.Exit()

    if clean:
        clean_dir()

    # use the agent to create tests
    agent(prompt, url)
