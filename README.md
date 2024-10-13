# Automators Agent


## Installation

Clone the repository:

```bash
git clone https://github.com/automators-com/agent.git
cd agent
```

Install the dependencies:

```bash
uv sync --all-extras --dev
```

Install playwright:
    
```bash
.venv/bin/playwright install chromium
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
uv run main.py
```