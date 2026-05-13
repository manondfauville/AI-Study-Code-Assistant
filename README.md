# AI Study & Code Assistant

A command-line AI assistant that helps users understand programming concepts
and debug Python code. Type a question or paste a snippet — the agent uses
tools to return a structured, helpful answer.

> **AI backend:** [Google Gemini API](https://aistudio.google.com/) (free tier).

---

## Project goal

This system targets learners and developers who want fast, contextual help
from their terminal. The two main use cases are:

- **Concept explanation** — ask about a programming topic and get a clear,
  up-to-date explanation backed by a live web search.
- **Code debugging** — paste a Python snippet and get a diagnosis with a
  suggested fix.

---

## How it works

A single intelligent agent powered by the Gemini API receives the user's
input and decides which tool to call:

1. **`web_search`** — fetches up-to-date documentation or explanations
   via `duckduckgo-search`.
2. **`analyse_code`** — statically analyses a Python snippet with `ast`
   (syntax check), then executes it in an isolated `subprocess` (runtime
   check).

The agentic loop continues until Gemini returns a plain-text answer, which
is printed to the terminal.

---

## Project structure

```
ai-study-assistant/
├── agent/
│   ├── __init__.py
│   ├── agent.py              # Core agent loop + tool dispatcher
│   └── tools.py              # web_search and analyse_code implementations
├── tests/
│   ├── conftest.py           # Pytest path setup
│   ├── test_tools.py         # Tool-layer unit tests (17 tests)
│   ├── test_agent.py         # Agent-layer unit tests (6 tests)
│   └── test_input_validation.py  # Edge-case / input tests (17 tests)
├── main.py                   # Entry point (REPL loop)
├── requirements.txt          # Python dependencies
├── Makefile                  # Convenience shortcuts
├── .env.example              # Environment variable template
├── .gitignore
└── README.md
```

---

## Requirements

- Python 3.10 or newer
- A [Gemini API key](https://aistudio.google.com/) (free tier is sufficient)

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/ai-study-assistant.git
cd ai-study-assistant

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
# or:  make install

# 4. Configure your API key
cp .env.example .env
# Edit .env and paste your key:  GEMINI_API_KEY=your_key_here
```

---

## Configuration

`.env` (copied from `.env.example`):

```
GEMINI_API_KEY=your_api_key_here
```

The key is loaded automatically by `python-dotenv` when `main.py` starts.
Never commit your `.env` file — it is listed in `.gitignore`.

---

## Usage

```bash
python main.py
# or:  make run
```

Type a question or paste a code snippet at the `>` prompt:

```
> What is a Python decorator?
> Why does this crash: for i in range(10) print(i)
> exit
```

Type `exit`, `quit`, or press `Ctrl-C` to quit.

---

## Running tests

```bash
pytest tests/ -v
# or:  make test
```

All 40 tests run without a real API key — Gemini calls are mocked where
needed, and `analyse_code` uses the local Python interpreter directly.

---

## Data flow

```
User input (plain text)
        │
        ▼
  main.py  ──►  agent.run(user_input)
                      │
                      ▼
              Gemini API  ──► decides which tool to call
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
    web_search(query)      analyse_code(snippet)
    returns plain text     returns plain text report
          │                       │
          └───────────┬───────────┘
                      ▼
              Gemini synthesises result
                      │
                      ▼
           Formatted answer printed to terminal
```

Data passed between components is always plain UTF-8 text. The Gemini API
accepts and returns JSON internally, but the agent layer exposes only Python
strings to the tools and to `main.py`.

---

## Deployment

The system is designed as a **local command-line tool**. It requires no
server, no database, and no persistent state.

For a production or team deployment the recommended path would be:

1. Package with `pyproject.toml` / `pip install -e .` so it is installable
   as a CLI tool.
2. Distribute via a private PyPI server or as a Docker image.
3. Run a staged rollout: local → shared dev environment → broader release,
   with tests passing at each stage before promotion.
4. Store the API key in a secrets manager (e.g. environment variable
   injected by the deployment platform) rather than a local `.env` file.

---

## Dependencies

| Package | Purpose |
|---|---|
| `google-genai` | Gemini API SDK — the agent brain |
| `duckduckgo-search` | Web search tool for concept lookups |
| `python-dotenv` | Loads `.env` into environment variables |
| `pytest` | Testing framework |

`ast` and `subprocess` are part of Python's standard library.

---

## Development status

| Stage | Due | Status |
|---|---|---|
| Step 1 — Design & planning | 24.04 | ✅ Done |
| Step 2 — Implementation | 08.05 | ✅ Done |
| Step 3 — Testing & deployment prep | 15.05 | ✅ Done |
| Final submission | 22.05 | 🔲 Upcoming |

---

## License

MIT
