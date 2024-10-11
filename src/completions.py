import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def generate_test_code(page: str, prompt: str, url: str):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "assistant",
                "content": "You are a useful testing agent. Your job is to analyse webpage content and create tests based on some user provided scope. You should only ever return the test code.",
            },
            {
                "role": "assistant",
                "content": "Only return valid test code which can be written to a single code file. Avoid imports and other code which would not be valid in a single file.",
            },
            {
                "role": "user",
                "content": f"Consider the following webpage content: {page} for {url}",
            },
            {
                "role": "user",
                "content": f"Consider the following scope: {prompt}",
            },
        ],
        model=os.environ.get("OPENAI_MODEL"),
    )

    return chat_completion
