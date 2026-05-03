"""
agent.py — Core agent logic for the AI Study & Code Assistant.

Uses the Google Gemini API (free tier) with the official google-genai SDK.
The agent sends the user's message to Gemini, which autonomously decides
whether to call web_search, analyse_code, or neither. Tool results are
fed back into the conversation until Gemini returns a final text answer.
"""

import os
from google import genai
from google.genai import types
from agent.tools import web_search, analyse_code

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODEL = "gemini-2.5-flash"   # Free tier, fast, supports tool use

SYSTEM_PROMPT = """\
You are a helpful programming study assistant running in a terminal.

You have two tools available:
  - web_search    : use when the user asks about a concept, keyword, or technology
  - analyse_code  : use when the user shares a Python snippet and wants debugging help

Rules:
  1. Always use a tool when it would improve your answer.
  2. After receiving a tool result, synthesise it into a clear, concise explanation.
  3. Format responses for a terminal: use plain text, no markdown headers, keep
     lines under ~90 characters where possible.
  4. Be encouraging and educational — explain *why*, not just *what*.
"""

# ---------------------------------------------------------------------------
# Tool definitions (google-genai format)
# ---------------------------------------------------------------------------

GEMINI_TOOLS = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="web_search",
                description=(
                    "Search the web for up-to-date information about programming "
                    "concepts, libraries, language features, or documentation."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "query": types.Schema(
                            type=types.Type.STRING,
                            description="The search query to look up.",
                        ),
                        "max_results": types.Schema(
                            type=types.Type.INTEGER,
                            description="Max number of results to return (default 4).",
                        ),
                    },
                    required=["query"],
                ),
            ),
            types.FunctionDeclaration(
                name="analyse_code",
                description=(
                    "Analyse a Python code snippet for syntax errors using ast, "
                    "then execute it in a subprocess to catch runtime errors."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "snippet": types.Schema(
                            type=types.Type.STRING,
                            description="The Python source code to analyse.",
                        ),
                    },
                    required=["snippet"],
                ),
            ),
        ]
    )
]

# ---------------------------------------------------------------------------
# Tool dispatcher
# ---------------------------------------------------------------------------

TOOL_FUNCTIONS: dict = {
    "web_search": web_search,
    "analyse_code": analyse_code,
}


def _dispatch_tool(tool_name: str, tool_input: dict) -> str:
    """Call the appropriate Python function for a tool call request."""
    fn = TOOL_FUNCTIONS.get(tool_name)
    if fn is None:
        return f"Unknown tool: {tool_name}"
    return fn(**tool_input)


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class StudyAgent:
    """
    A single-turn agent that processes one user query per call.

    The agentic loop:
      1. Send user message + tool definitions to Gemini.
      2. If Gemini requests a tool, run it and send the result back.
      3. Repeat until Gemini returns a plain-text response.
      4. Return that response to the caller.
    """

    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY is not set. "
                "Copy .env.example to .env and add your free key from "
                "https://aistudio.google.com/app/apikey"
            )
        self.client = genai.Client(api_key=api_key)

    def run(self, user_input: str) -> str:
        """
        Process a single user query and return the agent's final answer.

        Args:
            user_input: The raw text the user typed.

        Returns:
            A plain-text string with the agent's answer.
        """
        contents = [types.Content(
            role="user",
            parts=[types.Part(text=user_input)]
        )]

        # Agentic loop — continue until Gemini stops requesting tools
        while True:
            response = self.client.models.generate_content(
                model=MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    tools=GEMINI_TOOLS,
                ),
            )

            # Append Gemini's response to conversation history
            contents.append(response.candidates[0].content)

            # Check if any part is a function call
            function_calls = [
                part for part in response.candidates[0].content.parts
                if part.function_call is not None
            ]

            if not function_calls:
                # No tool calls — return the text response
                return response.text.strip() or "(No text response from agent.)"

            # Dispatch all tool calls and collect results
            tool_results = []
            for part in function_calls:
                fc = part.function_call
                result = _dispatch_tool(fc.name, dict(fc.args))
                tool_results.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=fc.name,
                            response={"result": result},
                        )
                    )
                )

            # Feed tool results back into the conversation
            contents.append(types.Content(role="user", parts=tool_results))
