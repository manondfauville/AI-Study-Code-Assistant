# AI Study & Code Assistant

A command-line AI assistant that helps users understand programming concepts and debug Python code. The user types a question or pastes a code snippet, and the agent uses tools to return a structured, helpful answer.

> **Note:** This project uses the [Google Gemini API](https://aistudio.google.com/) as its AI backend. A free API key is available via Google AI Studio.

---

## Project goal

This system targets learners and developers who want fast, contextual help from their terminal. The two main use cases are:

- **Concept explanation** — ask about a programming topic and get a clear, up-to-date explanation
- **Code debugging** — paste a Python snippet and get a diagnosis with a suggested fix

---

## How it works

The system uses a single intelligent agent powered by the [Google Gemini API](https://aistudio.google.com/). When the user submits input, the agent classifies the intent and calls the appropriate tool:

1. **Web search tool** — fetches up-to-date documentation or explanations (via `duckduckgo-search`)
2. **Code analysis tool** — statically analyses a Python snippet using `ast` and `subprocess`
3. **Output formatter** — structures the final response into a readable terminal output

---

## Project structure

```
ai-study-assistant/
├── agent/
│   ├── __init__.py
│   ├── agent.py          # Core agent logic
│   └── tools.py          # Tool definitions
├── tests/
│   └── test_tools.py     # Unit tests
├── main.py               # Entry point
├── requirements.txt      # Dependencies
├── .env.example          # Environment variable template
├── .gitignore
└── README.md
```

---

## Requirements

- Python 3.10+
- A [Gemini API key](https://aistudio.google.com/) (free tier available)

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/ai-study-assistant.git
cd ai-study-assistant

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your API key
cp .env.example .env
# Then edit .env and add your Anthropic API key
```

---

## Configuration

Create a `.env` file at the root of the project (copy from `.env.example`):

```
GEMINI_API_KEY=your_api_key_here
```

Never commit your `.env` file — it is already listed in `.gitignore`.

---

## Usage

```bash
python main.py
```

You will be prompted to type a question or paste a code snippet. Example inputs:

```
> What is recursion in Python?
> Why does this code crash: for i in range(10) print(i)
```

---

## Running tests

```bash
pytest tests/
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `google-generativeai` | Gemini API SDK — the agent brain |
| `duckduckgo-search` | Web search tool for concept lookups |
| `pytest` | Testing framework |

`ast` and `subprocess` are part of Python's standard library and require no installation.

---

## Development status

| Stage | Due | Status |
|---|---|---|
| Step 1 — Design & planning | 24.04 | ✅ Done |
| Step 2 — Implementation | 08.05 | 🔲 Upcoming |
| Step 3 — Testing & deployment prep | 15.05 | 🔲 Upcoming |
| Final submission | 22.05 | 🔲 Upcoming |

---

## License

MIT
