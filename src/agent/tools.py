import os
from playwright.sync_api import sync_playwright
from agent.setup import TEST_DIR
from agent.utils import run_pytest_and_capture_output, strip_code_fences
from agent.logging import logger, console
from rich.panel import Panel
from typing import TypedDict


# TODO: Consider adding pydantic for additional data validation
class TExtractWebpageContent(TypedDict):
    url: str


def extract_webpage_content(**kwargs: TExtractWebpageContent) -> str | None:
    url = kwargs.get("url", None)
    if not url:
        return logger.error("No URL provided to extract webpage content from.")

    logger.info(f"Extracting webpage content from {url}")
    content = None
    with sync_playwright() as p:
        logger.info("Launching browser")
        browser = p.chromium.launch(
            headless=os.environ.get("HEADLESS", False) == "true"
        )
        page = browser.new_page()
        logger.info(f"Visiting {url}")
        page.goto(url)
        logger.info("Waiting for page load state to be networkidle")
        page.wait_for_load_state("networkidle")
        logger.info("Page loaded! Extracting content.")
        content = page.content()
        page_file_name = f"{url.replace('https://', '').replace('http://', '').replace('/', '_')}.html"

        if os.environ.get("LOG_LEVEL", "INFO") == "DEBUG":
            logger.info(f"Writing content to {page_file_name}")
            with open(TEST_DIR / page_file_name, "w+") as f:
                f.write(content)

        logger.info("Closing browser")
        browser.close()

    return content


class TWriteCodeToFile(TypedDict):
    code: str
    file_name: str


def write_code_to_file(**kwargs: TWriteCodeToFile):
    code = kwargs.get("code", None)
    file_name = kwargs.get("file_name", "test_by_automators_agent.py")

    if not code:
        return logger.error("code or file_name not provided to write code to file.")

    logger.info(f"Writing code to file {file_name}")
    with open(TEST_DIR / file_name, "w+") as f:
        f.write(strip_code_fences(code))


def run_tests():
    logger.info("Running tests")
    output = run_pytest_and_capture_output(TEST_DIR)
    console.print("\n")
    console.print(Panel(output, title="Test Output", highlight=True, padding=(1, 1)))
    console.print("\n")
    return output


tools = [
    {
        "type": "function",
        "function": {
            "name": "run_tests",
            "description": "Runs the written tests in the 'tests' folder. Call this whenever you need to validate if the tests are working as expected.",
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_code_to_file",
            "description": "Writes the generated code to a file. Once the tests are written to the file, you will be able to run them using 'run_tests'. The file will be created in the 'tests' folder. We are using the w+ mode to write the file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The generated code to be written to a file. Should be plain text and not include code fences.",
                    },
                    "file_name": {
                        "type": "string",
                        "description": "The name of the file to write the code to. Including the file extension.",
                    },
                },
                "required": ["code", "file_name"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "extract_webpage_content",
            "description": "Extracts the content of a webpage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the webpage to extract content from.",
                    },
                },
                "required": ["url"],
                "additionalProperties": False,
            },
        },
    },
]
