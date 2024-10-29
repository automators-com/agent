import os
import typer
from typing_extensions import Annotated
from rich.console import Console
from agent.completions import agent
from agent.logging import logger
from agent.config import get_test_dir, read_config
from agent.scaffold import (
    check_for_cypress_installation,
    check_for_node,
    check_for_npm,
    check_for_playwright,
    check_for_playwright_browsers,
    scaffold_playwright,
    scaffold_cypress,
)

err_console = Console(stderr=True)


def start(
    prompt: Annotated[
        str, typer.Option(help="A prompt describing the scope of your tests.")
    ] = None,
    url: Annotated[
        str,
        typer.Option(help="A url that acts as an entrypoint to app you're testing."),
    ] = None,
    clean: Annotated[
        bool,
        typer.Option(
            help="Delete files from the relevant test output directory before starting the agent."
        ),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option(help="Enable debug mode for additional logs and file writing."),
    ] = False,
    headless: Annotated[
        bool,
        typer.Option(help="Run the browser in headless mode."),
    ] = False,
    language: Annotated[
        str,
        typer.Option(help="The programming language to generate tests in."),
    ] = "python",
    framework: Annotated[
        str,
        typer.Option(help="The framework to use for testing."),
    ] = "playwright",
):
    """Starts the test generation agent ✨"""

    config = read_config()

    # CLI args should take precedence over config file
    if prompt is not None:
        config["agent"]["prompt"] = prompt
    if url is not None:
        config["agent"]["url"] = url
    if headless:
        config["config"]["headless"] = headless
    if debug:
        config["config"]["log_level"] = "DEBUG"
    if clean:
        config["config"]["clean"] = clean
    if language != "python":
        config["config"]["language"] = language
    if framework != "playwright":
        config["config"]["framework"] = framework

    # perform actions based on config
    log_level = str(config["config"]["log_level"]).upper()

    # set a defualt log level if invalid
    if log_level not in ["DEBUG", "INFO", "WARN", "ERROR"]:
        log_level = "INFO"

    logger.setLevel(log_level)
    os.environ["LOG_LEVEL"] = log_level

    if str(config["config"]["headless"]).lower() == "true":
        os.environ["HEADLESS"] = "true"

    # set agent language and framework as env vars
    os.environ["AGENT_LANGUAGE"] = config["config"]["language"]
    os.environ["AGENT_FRAMEWORK"] = config["config"]["framework"]
    test_dir = get_test_dir()

    # raise an error if required config is missing
    for item in ["url", "prompt"]:
        if config["agent"].get(item) is None:
            err_console.print(
                f"Please set agent.{item} in the config.toml file or pass it as the --{item} CLI option."
            )
            raise typer.Exit()

    # setup the testing environment
    if config["config"]["language"] in ["javascript", "typescript"]:
        node_version = check_for_node()
        npm_version = check_for_npm()

        if not node_version or not npm_version:
            logger.error(
                "Node.js and npm is required to run the agent in JavaScript or TypeScript mode."
            )
            raise typer.Exit()

    # check if playwright is installed
    if config["config"]["framework"] == "playwright":
        playwright_version = check_for_playwright()
        if not playwright_version:
            logger.error("Playwright is required to run the agent in Playwright mode.")
            raise typer.Exit()

    # clean out the test directory
    if str(config["config"]["clean"]).lower() == "true":
        logger.info(f"Deleting files in the {test_dir} directory")
        os.popen(f"rm -rf {test_dir}/*").read()

        if config["config"]["framework"] == "playwright":
            scaffold_playwright(
                test_dir,
                language=config["config"]["language"],
                clean=config["config"]["clean"],
            )
            check_for_playwright_browsers(test_dir)

        if config["config"]["framework"] == "cypress":
            # TODO: Add support for TypeScript
            if config["config"]["language"].lower() == "typescript":
                logger.error("Cypress with TypeScript, is not currently supported.")
                raise typer.Exit()

            scaffold_cypress(test_dir, language=config["config"]["language"])
            check_for_cypress_installation(test_dir)

    # call the agent
    agent(
        prompt=config["agent"]["prompt"],
        url=config["agent"]["url"],
        language=config["config"]["language"],
        framework=config["config"]["framework"],
    )
