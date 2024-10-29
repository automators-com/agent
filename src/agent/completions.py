import json
import os
import typer
from openai import OpenAI
import agent.tools as tools
from agent.logging import logger
from agent.rich import print_in_panel, print_in_question_panel
from agent.utils import check_for_screenshots
from agent.config import SUPPORTED_LANGUAGES, get_test_dir


def language_prompt(language: str):
    if language.lower() not in SUPPORTED_LANGUAGES:
        logger.error(f"Language {language} not supported.")
        raise typer.Exit()
    return f"You should write tests using the {language} programming language."


def framework_prompt(framework: str, language: str = "python"):
    if framework == "playwright" and language == "python":
        return """Tests should be written using playwright. We are using the pytest-playwright plugin, so you don't need to create your own browser context. Use page.locator where possible - use classnames, ids, placeholders, visible text or even labels to find elements. Avoid using deprecated methods.

        The structure of each test should be as follows:
        
        ```
        from playwright.sync_api import Page

        def test_name(page: Page):
            # test code here
        
        ```
        """
    elif framework == "playwright":
        return """
        Tests should be written using playwright. Use page.locator where possible - use classnames, ids, placeholders, visible text or even labels to find elements. Avoid using deprecated methods. Avoid imports from any external libraries unless the user specifies it.

        The structure of each test should be as follows:
        ```
        import { test, expect } from '@playwright/test';

        test('has title', async ({ page }) => {
            await page.goto('https://playwright.dev/');

            // Expect a title "to contain" a substring.
            await expect(page).toHaveTitle(/Playwright/);
        });
        ```
        """
    elif framework == "cypress":
        return """
        Tests should be written using cypress. Avoid using deprecated methods. Avoid imports from any external libraries unless the user specifies it.

        The structure of each test should be as follows:
        ```
        describe('My First Test', () => {
            it('Gets, types and asserts', () => {
                cy.visit('https://example.cypress.io')

                cy.contains('type').click()

                // Should be on a new URL which
                // includes '/commands/actions'
                cy.url().should('include', '/commands/actions')

                // Get an input, type into it
                cy.get('.action-email').type('fake@email.com')

                //  Verify that the value has been updated
                cy.get('.action-email').should('have.value', 'fake@email.com')
            })
        })
        ```
        """
    else:
        return ""


def log_completion(res: dict):
    # try to get ai message content
    try:
        content = json.loads(res)["choices"][0]["message"]["content"]
    except KeyError:
        content = None

    # try to get tool function calls

    try:
        tool_calls = json.loads(res)["choices"][0]["message"]["tool_calls"]
    except KeyError:
        tool_calls = None

    # log info in a panel
    if content:
        print_in_panel(str(content), title="Agent Message")

    if tool_calls:
        # loop through tool calls and format them as python function calls
        for tool_call in tool_calls:
            name = tool_call["function"]["name"]
            kwargs = json.loads(tool_call["function"]["arguments"])
            # truncate any long arguments
            for key, value in kwargs.items():
                if len(str(value)) > 50:
                    kwargs[key] = f"{str(value)[:50]}..."

            print_in_panel(f"{name}({kwargs})", title="Tool Call Requested")


def create_completion(messages: list, client: OpenAI):
    response = client.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o"),
        messages=messages,
        tools=tools.tools,
        tool_choice="auto",
        temperature=0.3,
    )
    log_completion(response.to_json())
    tool_calls = response.choices[0].message.tool_calls
    if tool_calls is None:
        tool_calls = []

    return response, tool_calls


def agent(
    prompt: str, url: str, language: str = "python", framework: str = "playwright"
):
    client = None
    openai_api_key = os.environ.get("OPENAI_API_KEY")

    if openai_api_key is None:
        return logger.error(
            "No OpenAI API key found. Please set the [purple3]OPENAI_API_KEY[/purple3] environment variable."
        )

    client = OpenAI(api_key=openai_api_key)

    agent_working = True
    messages = []
    messages.append(
        {
            "role": "assistant",
            "content": "You are a useful test code writing agent. Use the supplied tools to create passing tests for the user.",
        },
    )
    messages.append(
        {
            "role": "assistant",
            "content": f"{language_prompt(language)} {framework_prompt(framework)}",
        }
    )
    messages.append(
        {
            "role": "assistant",
            "content": f"""If tests are not passing, consider using the tools to debug the issue. 
            - You can overwrite any code in the {get_test_dir()} folder using the relevant tools. Use links found on the webpage to determine if navigation to other pages are required. 
            - You can use the extract_webpage_content tool in place of navigation. 
            - Do not make assumptions about the app structure or redirects unless there are clear links to support it. If you need more context, add code to save screenshots to the 'test-results' folder and the run the tests. We will send you the screenshots.
            - If you need input from the user, always use the get_user_input tool.""",
        },
    )
    messages.append(
        {
            "role": "user",
            "content": f"Our webpage entry point is: {url}. Consider the following requirements: {prompt}",
        },
    )
    messages.append(
        {
            "role": "user",
            "content": f"Consider the following requirements: {prompt}",
        },
    )

    logger.info(
        "Starting agent. Set log level to [cadet_blue]DEBUG[/cadet_blue] to see full requests."
    )
    logger.debug(json.dumps(messages, indent=2))

    response, tool_calls = create_completion(messages, client)

    while agent_working:
        if tool_calls == []:
            logger.info("No obvious action to be taken.")
            # prompt the user for an additional prompt
            print_in_question_panel(
                """Please enter an additional prompt if you would like to give the agent more context. If you have no additional prompt, you can type exit to stop the agent.""",
                title="Additional Prompt",
            )
            user_input = typer.prompt("Additional Prompt")
            if user_input.lower() != "exit":
                messages.append(
                    {
                        "role": "user",
                        "content": user_input,
                    }
                )
                response, tool_calls = create_completion(messages, client)
            else:
                agent_working = False
                break

        for tool_call in tool_calls:
            name = tool_call.function.name
            kwargs = json.loads(tool_call.function.arguments)
            logger.debug(f"Calling tool: {name} with arguments: {kwargs}")

            function_call_output = getattr(tools, name)(**kwargs)
            messages.append(
                {
                    "role": "assistant",
                    "content": f"Called tool: {name} with arguments: {kwargs}. The function call output was: {function_call_output} ",
                }
            )
            if name == "run_tests":
                screenshots = check_for_screenshots()
                for screenshot in screenshots:
                    logger.info("Screenshot found. Adding to context.")
                    messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Screenshots were taken on test failure. Please review the screenshots below to help debug the failing tests.",
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{screenshot}"
                                    },
                                },
                            ],
                        }
                    )

            logger.debug(json.dumps(messages, indent=2))
            response, tool_calls = create_completion(messages, client)
