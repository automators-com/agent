from dotenv import load_dotenv

from src.completions import agent_create_tests
from src.logging import logger

logger.info("Loading environment variables")
load_dotenv()

entry_point = "https://dev.datamaker.app"


def main():
    # create a prompt for the agent
    prompt = "Write some headless python playwright tests for the user signup flow."
    # use the agent to create tests
    agent_create_tests(prompt, entry_point)


if __name__ == "__main__":
    main()

# TODO: Look into edge case handling https://platform.openai.com/docs/guides/function-calling/edge-cases
