"""
agent.py — Core agent logic for the AI Study & Code Assistant.

Uses the Google Gemini API (free tier) instead of a paid API.
The agent sends the user's message to Gemini, which autonomously decides
whether to call web_search, analyse_code, or neither.  Tool results are
fed back into the conversation until Gemini returns a final text answer.
"""

import os
import google.generativeai as genai
from agent.tools import web_search, analyse_code

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODEL = "gemini-1.5-flash"

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
# Tool definitions (Gemini format)
# ---------------------------------------------------------------------------

GEMINI_TOOLS = [
    genai.protos.Tool(
        function_declarations=[
            genai.protos.FunctionDeclaration(
                name="web_search",
                description=(
                    "Search the web for up-to-date information about programming "
                    "concepts, libraries, language features, or documentation."
                ),
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "query": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="The search query to look up.",
                        ),
                        "max_results": genai.protos.Schema(
                            type=genai.protos.Type.INTEGER,
                            description="Maximum number of results to return (default 4).",
                        ),
                    },
                    required=["query"],
                ),
            ),
            genai.protos.FunctionDeclaration(
                name="analyse_code",
                description=(
                    "Analyse a Python code snippet for syntax errors using ast, "
                    "then execute it in a subprocess to catch runtime errors."
                ),
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "snippet": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
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
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=MODEL,
            system_instruction=SYSTEM_PROMPT,
            tools=GEMINI_TOOLS,
        )

    def run(self, user_input: str) -> str:
        """
        Process a single user query and return the agent's final answer.

        Args:
            user_input: The raw text the user typed.

        Returns:
            A plain-text string with the agent's answer.
        """
        chat = self.model.start_chat()

        # Agentic loop continue until Gemini stops requesting tools
        message = user_input
        while True:
            response = chat.send_message(message)
            candidate = response.candidates[0]
            part = candidate.content.parts[0]

            # If Gemini called a tool, dispatch it and loop back
            if part.function_call.name:
                fn_name = part.function_call.name
                fn_args = dict(part.function_call.args)
                tool_result = _dispatch_tool(fn_name, fn_args)

                # Send the tool result back as a function response
                message = genai.protos.Content(
                    parts=[
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=fn_name,
                                response={"result": tool_result},
                            )
                        )
                    ]
                )
                continue

            # No tool call Gemini is done, return the text
            return response.text.strip() or "(No text response from agent.)"
