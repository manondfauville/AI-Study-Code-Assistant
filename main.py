"""
main.py Entry point for the AI Study & Code Assistant.

Run with:
    python main.py
"""

import sys
from dotenv import load_dotenv
from agent.agent import StudyAgent

# Load ANTHROPIC_API_KEY from .env if present
load_dotenv()

BANNER = """
╔══════════════════════════════════════════════════════╗
║          AI Study & Code Assistant  v0.1             ║
║  Type a question or paste a Python snippet.          ║
║  Type  'exit' or press Ctrl-C to quit.               ║
╚══════════════════════════════════════════════════════╝
"""

DIVIDER = "─" * 60


def main() -> None:
    print(BANNER)

    try:
        agent = StudyAgent()
    except EnvironmentError as err:
        print(f"[Error] {err}")
        sys.exit(1)

    while True:
        try:
            user_input = input("\n> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit", "q"}:
            print("Goodbye!")
            break

        print(f"\n{DIVIDER}")
        print("Thinking…\n")

        try:
            answer = agent.run(user_input)
            print(answer)
        except Exception as err:
            print(f"[Agent error] {err}")

        print(DIVIDER)


if __name__ == "__main__":
    main()
