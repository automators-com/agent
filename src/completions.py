import json
import os
from openai import OpenAI
import src.tools as tools
from src.logging import logger

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def agent_create_tests(prompt: str, url: str):
    agent_working = True
    messages = []
    messages.append(
        {
            "role": "assistant",
            "content": "You are a useful test code writing agent. Use the supplied tools to create passing tests for the user. You are not able to ask the user for additional input after the initial prompt.",
        },
    )
    messages.append(
        {
            "role": "assistant",
            "content": "If tests are not passing, consider using the tools to debug the issue. You can overwrite any code in the out folder using the relevant tools. Use links found on the webpage to determine if navigation to other pages are required. You can use the extract_webpage_content tool in place of navigation. Do not make assumptions about the app structure or redirects unless there are clear links to support it.",
        },
    )
    messages.append(
        {
            "role": "user",
            "content": f"Our webpage entry point is: {url}",
        },
    )
    messages.append(
        {
            "role": "user",
            "content": f"Consider the following requirements: {prompt}",
        },
    )

    logger.info(
        "Making initial agent request. Set log level to DEBUG to see the full request."
    )
    logger.debug(json.dumps(messages, indent=2))

    response = client.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL"),
        messages=messages,
        tools=tools.tools,
        temperature=0.5,
    )

    logger.info(f"AGENT: {response.to_json()}")
    tool_calls = response.choices[0].message.tool_calls

    while agent_working:
        if tool_calls == [] or tool_calls is None:
            logger.info("No tool calls returned. Exiting.")
            agent_working = False
            break

        for tool_call in tool_calls:
            name = tool_call.function.name
            kwargs = json.loads(tool_call.function.arguments)
            logger.info(f"Calling tool: {name} with arguments: {kwargs}")

            function_call_output = getattr(tools, name)(**kwargs)
            messages.append(
                {
                    "role": "assistant",
                    "content": f"Called tool: {name} with arguments: {kwargs}. The function call output was: {function_call_output} ",
                }
            )

            logger.debug(json.dumps(messages, indent=2))
            response = client.chat.completions.create(
                model=os.environ.get("OPENAI_MODEL"),
                messages=messages,
                tools=tools.tools,
                temperature=0.5,
            )
            logger.info(f"AGENT: {response.to_json()}")
            tool_calls = response.choices[0].message.tool_calls
