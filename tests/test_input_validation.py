"""
tests/test_input_validation.py — Tests for input edge cases.

Covers whitespace-only input, very long input, special characters,
and non-ASCII text passed to the tool functions.

Run with:
    pytest tests/
"""

from unittest.mock import patch, MagicMock
from agent.tools import web_search, analyse_code


class TestInputEdgeCases:

    # ── web_search edge cases ───────────────────────────────

    def test_empty_query_string(self):
        """Empty query string is handled without raising."""
        with patch("agent.tools.DDGS") as mock_ddgs_cls:
            mock_ddgs = MagicMock()
            mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
            mock_ddgs.text.return_value = []
            result = web_search("")
        assert isinstance(result, str)

    def test_whitespace_only_query(self):
        """A whitespace-only query is handled without raising."""
        with patch("agent.tools.DDGS") as mock_ddgs_cls:
            mock_ddgs = MagicMock()
            mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
            mock_ddgs.text.return_value = []
            result = web_search("   ")
        assert isinstance(result, str)

    def test_special_characters_in_query(self):
        """Special characters in the query do not cause an exception."""
        with patch("agent.tools.DDGS") as mock_ddgs_cls:
            mock_ddgs = MagicMock()
            mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
            mock_ddgs.text.return_value = []
            result = web_search("C++ & Python <comparison> 'performance'")
        assert isinstance(result, str)

    def test_unicode_query(self):
        """Non-ASCII (Unicode) characters in a query do not cause an exception."""
        with patch("agent.tools.DDGS") as mock_ddgs_cls:
            mock_ddgs = MagicMock()
            mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
            mock_ddgs.text.return_value = []
            result = web_search("Python Ünterricht für Anfänger")
        assert isinstance(result, str)

    def test_very_long_query(self):
        """A very long query string is handled without raising."""
        with patch("agent.tools.DDGS") as mock_ddgs_cls:
            mock_ddgs = MagicMock()
            mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
            mock_ddgs.text.return_value = []
            result = web_search("python " * 200)
        assert isinstance(result, str)

    # ── analyse_code edge cases ────────────────────────────

    def test_whitespace_only_snippet(self):
        """A snippet of only whitespace is valid Python (no statements)."""
        result = analyse_code("   \n   \n")
        assert "Syntax check: PASSED" in result

    def test_comment_only_snippet(self):
        """A snippet containing only a comment is valid Python."""
        result = analyse_code("# just a comment")
        assert "Syntax check: PASSED" in result

    def test_very_long_valid_snippet(self):
        """A long but valid snippet is handled without raising."""
        snippet = "\n".join(f"x_{i} = {i}" for i in range(200))
        result = analyse_code(snippet)
        assert "Syntax check: PASSED" in result

    def test_unicode_string_in_snippet(self):
        """A snippet with Unicode string literals runs correctly."""
        result = analyse_code("print('héllo wörld')")
        assert "Runtime check: PASSED" in result

    def test_snippet_with_imports(self):
        """A snippet that imports a stdlib module runs correctly."""
        result = analyse_code("import math\nprint(math.pi)")
        assert "Runtime check: PASSED" in result
        assert "3.14" in result

    def test_snippet_with_multiline_string(self):
        """A snippet containing a multi-line string is parsed correctly."""
        snippet = 'text = """hello\nworld"""\nprint(text)'
        result = analyse_code(snippet)
        assert "Syntax check: PASSED" in result
