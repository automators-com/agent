import typer
from agent.cli import init, start

app = typer.Typer(name="agent", rich_markup_mode="markdown")
app.command(short_help="Scaffold new project.")(init.init)
app.command(short_help="Start the agent.")(start.start)


if __name__ == "__main__":
    app()
