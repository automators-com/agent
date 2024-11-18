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

    # TODO: Make this more robust
    # get language from environment
    language = os.environ.get("AGENT_LANGUAGE", "python")
    # get framework from environment
    framework = os.environ.get("AGENT_FRAMEWORK", "playwright")

    invalid_characters = ["\\", "/", ":", "*", "#", "?", '"', "'" "<", ">", "|"]
    # check file_name for invalid characters

    for char in invalid_characters:
        if char in file_name:
            return f"Invalid file name. Please provide a valid file name without any of the following invalid characters. {invalid_characters}"

    file_extension = ".py"

    if language == "typescript":
        file_extension = ".ts"
        if framework == "cypress":
            file_extension = ".cy.ts"
        elif framework == "playwright":
            file_extension = ".spec.ts"
    elif language == "javascript":
        file_extension = ".js"
        if framework == "cypress":
            file_extension = ".cy.js"
        elif framework == "playwright":
            file_extension = ".spec.js"

    if not file_name.endswith(file_extension):
        return f"Invalid language or file extension provided. Please rewrite the code in {language} and use a {file_extension} extension."

    out_dir = get_test_dir()

    if framework == "cypress":
        out_dir = out_dir / "e2e"
        # ensure the tests directory exists
        out_dir.mkdir(exist_ok=True)
    elif framework == "playwright":
        # ensure the tests directory exists
        out_dir = out_dir / "tests"
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
        output = run_playwright(test_dir / "tests")
        print_in_panel(output, "Test Output")
        return output
    elif language == "javascript" and framework == "playwright":
        output = run_playwright(test_dir / "tests")
        print_in_panel(output, "Test Output")
        return output
    elif language == "typescript" and framework == "cypress":
        output = run_cypress(test_dir, config_file_name="cypress.config.ts")
        print_in_panel(output, "Test Output")
        return output
    elif language == "javascript" and framework == "cypress":
        output = run_cypress(test_dir, config_file_name="cypress.config.js")
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


class TListFiles(TypedDict):
    dir: str


def list_files_in_dir(**kwargs: TListFiles) -> str:
    dir = kwargs.get("dir", ".")

    if not dir:
        return "No directory provided to list files in."

    # check if the directory exists
    if not os.path.exists(dir):
        return f"Directory {dir} does not exist."

    files = os.listdir(dir)
    return files


class TReadFileContents(TypedDict):
    path: str


def read_file_contents(**kwargs: TReadFileContents) -> str:
    path = kwargs.get("path", None)

    if not path:
        return "No path provided to read file contents from."

    if not os.path.exists(path):
        return f"File {path} does not exist."

    with open(path, "r") as f:
        return f.read()


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
    {
        "type": "function",
        "function": {
            "name": "list_files_in_dir",
            "description": "Lists the files in a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dir": {
                        "type": "string",
                        "description": "The directory to list files in.",
                    },
                },
                "required": ["dir"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file_contents",
            "description": "Reads the contents of a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path of the file to read contents from.",
                    },
                },
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    },
]
