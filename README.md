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

## Usage

Run the agent:

```bash
uv run main.py
```