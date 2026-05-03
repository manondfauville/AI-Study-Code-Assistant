"""
tests/test_tools.py Unit tests for the tool layer.

Run with:
    pytest tests/
"""

import pytest
from unittest.mock import patch, MagicMock
from agent.tools import web_search, analyse_code


# ─────────────────────────────────────────────────────────────
# web_search tests
# ─────────────────────────────────────────────────────────────

class TestWebSearch:

    def test_returns_string(self):
        """web_search always returns a string."""
        with patch("agent.tools.DDGS") as mock_ddgs_cls:
            mock_ddgs = MagicMock()
            mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
            mock_ddgs.text.return_value = [
                {"title": "Python recursion", "href": "https://example.com", "body": "Recursion explanation."}
            ]
            result = web_search("Python recursion")
        assert isinstance(result, str)

    def test_result_contains_url(self):
        """Result string includes the URL from the search result."""
        with patch("agent.tools.DDGS") as mock_ddgs_cls:
            mock_ddgs = MagicMock()
            mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
            mock_ddgs.text.return_value = [
                {"title": "Example", "href": "https://docs.python.org", "body": "Python docs."}
            ]
            result = web_search("Python docs")
        assert "https://docs.python.org" in result

    def test_no_results(self):
        """Returns a friendly message when there are no results."""
        with patch("agent.tools.DDGS") as mock_ddgs_cls:
            mock_ddgs = MagicMock()
            mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
            mock_ddgs.text.return_value = []
            result = web_search("aslkdjaslkdj_nonsense_query_xyz")
        assert "No results" in result

    def test_exception_handled(self):
        """Network failure returns an error string instead of raising."""
        with patch("agent.tools.DDGS") as mock_ddgs_cls:
            mock_ddgs_cls.side_effect = Exception("network error")
            result = web_search("anything")
        assert "failed" in result.lower()


# ─────────────────────────────────────────────────────────────
# analyse_code tests
# ─────────────────────────────────────────────────────────────

class TestAnalyseCode:

    def test_valid_code_passes(self):
        """A correct snippet passes both syntax and runtime checks."""
        result = analyse_code("x = 1 + 1\nprint(x)")
        assert "Syntax check: PASSED" in result
        assert "Runtime check: PASSED" in result

    def test_syntax_error_detected(self):
        """A syntax error is caught before execution."""
        result = analyse_code("for i in range(10) print(i)")
        assert "Syntax check: FAILED" in result
        assert "SyntaxError" in result

    def test_runtime_error_detected(self):
        """A runtime error (ZeroDivisionError) is caught by subprocess."""
        result = analyse_code("x = 1 / 0")
        assert "Runtime check: FAILED" in result
        assert "ZeroDivisionError" in result

    def test_name_error_detected(self):
        """An undefined variable (NameError) is caught at runtime."""
        result = analyse_code("print(undefined_variable)")
        assert "Runtime check: FAILED" in result
        assert "NameError" in result

    def test_output_captured(self):
        """stdout from the snippet appears in the report."""
        result = analyse_code("print('hello world')")
        assert "hello world" in result

    def test_timeout_handled(self):
        """An infinite loop is stopped by the timeout guard."""
        result = analyse_code("while True: pass")
        assert "TIMED OUT" in result

    def test_returns_string(self):
        """analyse_code always returns a string."""
        assert isinstance(analyse_code("pass"), str)

    def test_empty_snippet(self):
        """An empty snippet is valid Python and passes both checks."""
        result = analyse_code("")
        assert "Syntax check: PASSED" in result
