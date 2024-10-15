import typer
from typing import Optional
from agent.completions import agent
from typing_extensions import Annotated
from agent.config import clean_dir, setup


__app_name__ = "agent"
__version__ = "0.1.0"

setup()


def version_callback(value: bool):
    if value:
        print(f"Automators Agent CLI Version: {__version__}")
        raise typer.Exit()


app = typer.Typer()


@app.command()
def main(
    prompt: Annotated[
        str,
        typer.Option(help="A prompt describing the scope of your tests."),
    ],
    url: Annotated[
        str,
        typer.Option(help="A url that acts as an entrypoint to app you're testing."),
    ],
    clean: Annotated[
        bool, typer.Option(help="Clean the out directory before running the tests.")
    ] = False,
    version: Annotated[
        Optional[bool], typer.Option("--version", callback=version_callback)
    ] = None,
):
    if clean:
        clean_dir()

    # use the agent to create tests
    agent(prompt, url)


if __name__ == "__main__":
    app()
