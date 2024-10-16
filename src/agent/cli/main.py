import typer
from rich import print
from agent.cli import init, start
from agent import __version__

app = typer.Typer(name="agent", rich_markup_mode="markdown")
app.command(short_help="Scaffold new project.")(init.init)
app.command(short_help="Start the agent.")(start.start)


def version_callback(value: bool):
    if value:
        print(
            f"Automators Agent CLI Version:  [medium_spring_green]{__version__}[/medium_spring_green]"
        )
        raise typer.Exit()


@app.callback()
def common(
    ctx: typer.Context,
    version: bool = typer.Option(None, "--version", callback=version_callback),
):
    pass


if __name__ == "__main__":
    app()
