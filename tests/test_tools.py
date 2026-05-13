"""
tests/test_tools.py — Unit tests for the tool layer.

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

    def test_result_contains_title(self):
        """Result string includes the title from the search result."""
        with patch("agent.tools.DDGS") as mock_ddgs_cls:
            mock_ddgs = MagicMock()
            mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
            mock_ddgs.text.return_value = [
                {"title": "My Title", "href": "https://example.com", "body": "Some body."}
            ]
            result = web_search("my query")
        assert "My Title" in result

    def test_result_contains_body_snippet(self):
        """Result string includes the body snippet from the search result."""
        with patch("agent.tools.DDGS") as mock_ddgs_cls:
            mock_ddgs = MagicMock()
            mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
            mock_ddgs.text.return_value = [
                {"title": "T", "href": "https://x.com", "body": "Unique snippet content here."}
            ]
            result = web_search("query")
        assert "Unique snippet content here." in result

    def test_multiple_results_numbered(self):
        """Multiple results are returned with numbering."""
        with patch("agent.tools.DDGS") as mock_ddgs_cls:
            mock_ddgs = MagicMock()
            mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
            mock_ddgs.text.return_value = [
                {"title": "First", "href": "https://a.com", "body": "A"},
                {"title": "Second", "href": "https://b.com", "body": "B"},
            ]
            result = web_search("query", max_results=2)
        assert "[1]" in result
        assert "[2]" in result

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

    def test_max_results_respected(self):
        """max_results limits how many results are requested from DDGS."""
        with patch("agent.tools.DDGS") as mock_ddgs_cls:
            mock_ddgs = MagicMock()
            mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
            mock_ddgs.text.return_value = []
            web_search("query", max_results=2)
            mock_ddgs.text.assert_called_once_with("query", max_results=2)

    def test_missing_fields_handled(self):
        """Results with missing title/href/body don't raise an exception."""
        with patch("agent.tools.DDGS") as mock_ddgs_cls:
            mock_ddgs = MagicMock()
            mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
            mock_ddgs.text.return_value = [{}]
            result = web_search("query")
        assert isinstance(result, str)


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

    def test_syntax_error_skips_runtime(self):
        """When syntax fails, runtime check is not attempted."""
        result = analyse_code("def broken(")
        assert "Syntax check: FAILED" in result
        assert "Runtime check" not in result

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

    def test_index_error_detected(self):
        """An IndexError is caught at runtime."""
        result = analyse_code("lst = [1, 2]\nprint(lst[99])")
        assert "Runtime check: FAILED" in result
        assert "IndexError" in result

    def test_type_error_detected(self):
        """A TypeError is caught at runtime."""
        result = analyse_code("'hello' + 5")
        assert "Runtime check: FAILED" in result
        assert "TypeError" in result

    def test_output_captured(self):
        """stdout from the snippet appears in the report."""
        result = analyse_code("print('hello world')")
        assert "hello world" in result

    def test_multiline_output_captured(self):
        """Multiple printed lines appear in the report."""
        result = analyse_code("for i in range(3):\n    print(i)")
        assert "0" in result
        assert "1" in result
        assert "2" in result

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

    def test_report_header_present(self):
        """The report always starts with the section header."""
        result = analyse_code("x = 1")
        assert "Code Analysis Report" in result

    def test_multiline_valid_code(self):
        """Multi-line valid code with function definition passes."""
        snippet = (
            "def add(a, b):\n"
            "    return a + b\n"
            "print(add(2, 3))"
        )
        result = analyse_code(snippet)
        assert "Syntax check: PASSED" in result
        assert "Runtime check: PASSED" in result
        assert "5" in result
