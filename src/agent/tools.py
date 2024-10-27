import os
import typer
from playwright.sync_api import sync_playwright
from agent.config import get_test_dir
from agent.rich import print_in_panel, print_in_question_panel
from agent.utils import (
    run_cypress,
    run_playwright,
    run_pytest_playwright,
    strip_code_fences,
)
from agent.logging import logger
from typing import TypedDict
from bs4 import BeautifulSoup


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
        logger.info("Waiting for page load state to be domcontentloaded")
        page.wait_for_load_state("domcontentloaded")
        logger.info("Page loaded! Extracting content.")
        content = page.content()

        # use beautiful soup to extract the body only
        soup = BeautifulSoup(content, "html.parser")
        # delete the head tag
        soup.head.extract()
        # delete the script tags
        for script in soup.find_all("script"):
            script.extract()

        content = str(soup)

        page_file_name = f"{url.replace('https://', '').replace('http://', '').replace('/', '_')}.html"

        if os.environ.get("LOG_LEVEL", "INFO") == "DEBUG":
            logger.info(f"Writing content to {page_file_name}")
            test_dir = get_test_dir()
            with open(test_dir / page_file_name, "w+") as f:
                f.write(content)

        logger.info("Closing browser")
        browser.close()

    return content


class TWriteCodeToFile(TypedDict):
    code: str
    file_name: str


def write_code_to_file(**kwargs: TWriteCodeToFile):
    code = kwargs.get("code", None)
    file_name = kwargs.get("file_name", None)

    if not code or not file_name:
        error_message = "code or file_name not provided to write code to file."
        logger.error(error_message)
        return error_message

    # get language from environment
    language = os.environ.get("AGENT_LANGUAGE", "python")

    if language == "python" and not file_name.endswith(".py"):
        return "Invalid language or file extension provided. Please rewrite the code in python and use a .py extension."
    elif language == "typescript" and not file_name.endswith(".spec.ts"):
        return "Invalid language or file extension provided. Please rewrite the code in typescript and use a .spec.ts extension."
    elif language == "javascript" and not file_name.endswith(".spec.js"):
        return "Invalid language or file extension provided. Please rewrite the code in javascript and use a .spec.js extension."

    out_dir = get_test_dir()

    if language == "typescript" or language == "javascript":
        out_dir = out_dir / "tests"
        # ensure the tests directory exists
        out_dir.mkdir(exist_ok=True)

    logger.info(f"Writing code to file {file_name}")
    with open(out_dir / file_name, "w+") as f:
        f.write(strip_code_fences(code))
        return f"Code written to {file_name}"


def run_tests():
    # ensure the tests directory exists
    test_dir = get_test_dir()
    test_dir.mkdir(exist_ok=True)
    logger.info("Running tests")

    # get the language and framework from the environment
    language = os.environ.get("AGENT_LANGUAGE", "python")
    framework = os.environ.get("AGENT_FRAMEWORK", "playwright")
    if language == "python" and framework == "playwright":
        # run the tests and capture the output
        output = run_pytest_playwright(test_dir)
        # print output in a panel
        print_in_panel(output, "Test Output")
        return output

    elif language == "typescript" and framework == "playwright":
        output = run_playwright(test_dir)
        print_in_panel(output, "Test Output")
        return output
    elif language == "javascript" and framework == "playwright":
        output = run_playwright(test_dir)
        print_in_panel(output, "Test Output")
        return output
    elif language == "typescript" and framework == "cypress":
        output = run_cypress(test_dir)
        print_in_panel(output, "Test Output")
        return output
    elif language == "javascript" and framework == "cypress":
        output = run_cypress(test_dir)
        print_in_panel(output, "Test Output")
        return output
    else:
        return "Not possible to run tests."


class TGetUserInput(TypedDict):
    question: str


def get_user_input(**kwargs: TGetUserInput) -> str:
    question = kwargs.get("question", None)

    if not question:
        return logger.error("No question provided to get user input for.")

    print_in_question_panel(question)
    response = typer.prompt("Response")

    return response


tools = [
    {
        "type": "function",
        "function": {
            "name": "run_tests",
            "description": f"Runs the written tests in the '{get_test_dir()}' folder. Call this whenever you need to validate if the tests are working as expected.",
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_code_to_file",
            "description": f"Writes the generated code to a file. Once the tests are written to the file, you will be able to run them using 'run_tests'. The file will be created in the '{get_test_dir()}' folder. We are using the w+ mode to write the file.",
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
    {
        "type": "function",
        "function": {
            "name": "get_user_input",
            "description": "Prompts the user for input. Use this tool to get input from the user when needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to ask the user for input.",
                    },
                },
                "required": ["question"],
                "additionalProperties": False,
            },
        },
    },
]
