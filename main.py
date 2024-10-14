from dotenv import load_dotenv

from src.completions import agent_create_tests
from src.logging import logger

logger.info("Loading environment variables")
load_dotenv()

entry_point = "https://dev.datamaker.app"
prompt = "Please write tests for me using Playwright and Python. I want you to test the signup flow and then the sign-in flow using the same user. Start with testuser123@automators.com as your user. Randomize the username on every test run. Expect a redirect /dashboard after sign-in."


def main():
    # use the agent to create tests
    agent_create_tests(prompt, entry_point)


if __name__ == "__main__":
    main()

# TODO: Look into edge case handling https://platform.openai.com/docs/guides/function-calling/edge-cases
