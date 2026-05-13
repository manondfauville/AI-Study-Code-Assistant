"""
tests/test_agent.py — Unit tests for the agent layer.

Tests focus on the tool-dispatch logic and agent behaviour
without making real API calls (all Gemini calls are mocked).

Run with:
    pytest tests/
"""

import pytest
from unittest.mock import MagicMock, patch
from agent.agent import _dispatch_tool, TOOL_FUNCTIONS


# ─────────────────────────────────────────────────────────────
# _dispatch_tool tests
# ─────────────────────────────────────────────────────────────

class TestDispatchTool:

    def test_dispatch_web_search(self):
        """web_search is routed to the correct function."""
        with patch.dict(TOOL_FUNCTIONS, {"web_search": MagicMock(return_value="search result")}):
            result = _dispatch_tool("web_search", {"query": "Python lists"})
        assert result == "search result"

    def test_dispatch_analyse_code(self):
        """analyse_code is routed to the correct function."""
        with patch.dict(TOOL_FUNCTIONS, {"analyse_code": MagicMock(return_value="analysis result")}):
            result = _dispatch_tool("analyse_code", {"snippet": "print('hi')"})
        assert result == "analysis result"

    def test_dispatch_unknown_tool(self):
        """An unknown tool name returns an error string, not an exception."""
        result = _dispatch_tool("nonexistent_tool", {})
        assert "Unknown tool" in result

    def test_dispatch_passes_kwargs(self):
        """Arguments are forwarded to the tool function correctly."""
        mock_fn = MagicMock(return_value="ok")
        with patch.dict(TOOL_FUNCTIONS, {"web_search": mock_fn}):
            _dispatch_tool("web_search", {"query": "closures", "max_results": 2})
        mock_fn.assert_called_once_with(query="closures", max_results=2)


# ─────────────────────────────────────────────────────────────
# StudyAgent initialisation tests
# ─────────────────────────────────────────────────────────────

class TestStudyAgentInit:

    def test_missing_api_key_raises(self):
        """StudyAgent raises EnvironmentError when GEMINI_API_KEY is absent."""
        with patch.dict("os.environ", {}, clear=True):
            # Remove the key if present
            import os
            os.environ.pop("GEMINI_API_KEY", None)
            from agent.agent import StudyAgent
            with pytest.raises(EnvironmentError, match="GEMINI_API_KEY"):
                StudyAgent()

    def test_agent_created_with_key(self):
        """StudyAgent initialises without error when the API key is set."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "fake-key-for-testing"}):
            with patch("agent.agent.genai.Client"):
                from agent.agent import StudyAgent
                agent = StudyAgent()
                assert agent is not None
