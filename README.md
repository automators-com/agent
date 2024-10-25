# Automators Agent

## Pre-requisites

Before you begin, ensure that you have [pipx](https://pipx.pypa.io/stable/installation) installed.

> **Note:** Python 3.13 (which the default homebrew pipx install depends on) is not yet supported by us (see https://github.com/automators-com/agent/issues/7). We would suggest using `pip install pipx` in the interim.

You also need to have playwright installed:

```bash
pip install --upgrade pip
pip install playwright
playwright install
```

## Installation

1. Install the agent using pipx:

```bash
python -m pipx install automators-agent
```
    
2. Initialize the agent:

```bash
agent init
```

3. Update the `.env` file to include an OpenAI API key. Edit the prompt in the `config.toml` file and then start the agent:

```bash
agent start
```

## Setting up development environment

Clone the repository:

```bash
git clone https://github.com/automators-com/agent.git
cd agent
```

Install the dependencies:

```bash
pip install uv
uv sync --all-extras --dev
```

Install playwright:
    
```bash
playwright install chromium
# npx playwright install chromium
```

## Environment Variables

Create a `.env` file in the root of the project with the following content:

```bash
OPENAI_API_KEY=""
OPENAI_MODEL="gpt-4o"
HEADLESS=true
LOG_LEVEL="INFO"
```

## Usage

Run the agent:

```bash
uv run agent start
```