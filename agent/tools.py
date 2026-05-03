"""
tools.py — Tool definitions for the AI Study & Code Assistant.

Two tools are available to the agent:
  1. web_search       fetches up-to-date explanations using DuckDuckGo
  2. analyse_code     statically checks a Python snippet with ast and optionally
                       runs it with subprocess to surface runtime errors
"""

import ast
import subprocess
import sys
import textwrap
from duckduckgo_search import DDGS


# ---------------------------------------------------------------------------
# Tool 1: Web search
# ---------------------------------------------------------------------------

def web_search(query: str, max_results: int = 4) -> str:
    """
    Search the web for programming concepts or documentation.

    Args:
        query:       Natural-language search query.
        max_results: How many results to include (default 4).

    Returns:
        A formatted string containing titles, URLs, and snippets.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            return "No results found for that query."

        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"[{i}] {r.get('title', 'No title')}")
            lines.append(f"    URL: {r.get('href', '')}")
            lines.append(f"    {r.get('body', '')}\n")

        return "\n".join(lines)

    except Exception as exc:
        return f"Web search failed: {exc}"


# ---------------------------------------------------------------------------
# Tool 2: Python code analysis
# ---------------------------------------------------------------------------

def analyse_code(snippet: str) -> str:
    """
    Analyse a Python code snippet for syntax and runtime errors.

    Steps:
      1. Attempt to parse the snippet with ast.parse (catches SyntaxError).
      2. If parsing succeeds, execute the snippet in a subprocess with a 10-
         second timeout and capture stdout / stderr.

    Args:
        snippet: A string containing Python source code.

    Returns:
        A structured diagnostic report as plain text.
    """
    report_lines = ["=== Code Analysis Report ===\n"]

    # -- Step 1: Syntax check via AST ------------------------------------
    try:
        ast.parse(snippet)
        report_lines.append("Syntax check: PASSED — no syntax errors detected.\n")
    except SyntaxError as err:
        report_lines.append("Syntax check: FAILED")
        report_lines.append(f"   SyntaxError on line {err.lineno}: {err.msg}")
        if err.text:
            report_lines.append(f"   Problematic code: {err.text.rstrip()}")
        report_lines.append("\nFix: Review the line above and check for missing colons,")
        report_lines.append(" brackets, or quotation marks.\n")
        # No point running the code if it can't be parsed
        return "\n".join(report_lines)

    # -- Step 2: Runtime check via subprocess ----------------------------
    report_lines.append("Runtime check: executing snippet in isolated process…\n")
    try:
        result = subprocess.run(
            [sys.executable, "-c", snippet],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            report_lines.append("Runtime check: PASSED — code ran without errors.")
            if result.stdout.strip():
                report_lines.append(f"\nOutput:\n{textwrap.indent(result.stdout.strip(), '   ')}")
        else:
            report_lines.append("Runtime check: FAILED")
            if result.stderr.strip():
                report_lines.append(f"\nError output:\n{textwrap.indent(result.stderr.strip(), '   ')}")
            report_lines.append("\nTip: Read the traceback from the bottom up to find")
            report_lines.append(" the root cause of the error.\n")

    except subprocess.TimeoutExpired:
        report_lines.append("Runtime check: TIMED OUT after 10 seconds.")
        report_lines.append("Your code may contain an infinite loop or blocking call.\n")
    except Exception as exc:
        report_lines.append(f"Runtime check could not be completed: {exc}\n")

    return "\n".join(report_lines)


# ---------------------------------------------------------------------------
# Tool schema passed to the Claude API as the tools parameter
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = [
    {
        "name": "web_search",
        "description": (
            "Search the web for up-to-date information about programming concepts, "
            "libraries, language features, or documentation. Use this when the user "
            "asks a question about a concept, keyword, or technology."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look up.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default 4).",
                    "default": 4,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "analyse_code",
        "description": (
            "Statically analyse a Python code snippet using the ast module to detect "
            "syntax errors, then execute it in a subprocess to catch runtime errors. "
            "Use this when the user shares Python code and wants to know why it fails "
            "or how to fix it."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "snippet": {
                    "type": "string",
                    "description": "The Python source code to analyse.",
                },
            },
            "required": ["snippet"],
        },
    },
]
