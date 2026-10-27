import unittest
from render.index_model import IndexValidationError, validate_index
from render.index_html import render_index

TWO = {
    "papers": [
        {"title": "Beta", "authors": "Ji", "year": 2024, "url": "https://example.org/b", "venue": "MODELS"},
        {"title": "Alpha", "authors": "Gower", "year": 2026, "url": "https://example.org/a"},
    ]
}


class IndexValidateTests(unittest.TestCase):
    def test_missing_url_names_url(self):
        doc = {"papers": [{"title": "T", "authors": "A", "year": 2026}]}
        with self.assertRaises(IndexValidationError) as cm:
            validate_index(doc)
        self.assertIn("url", "\n".join(cm.exception.messages))

    def test_duplicate_url(self):
        doc = {"papers": [
            {"title": "A", "authors": "A", "year": 2026, "url": "https://example.org/a"},
            {"title": "B", "authors": "B", "year": 2025, "url": "https://example.org/a"},
        ]}
        with self.assertRaises(IndexValidationError):
            validate_index(doc)

    def test_http_url_fails(self):
        doc = {"papers": [{"title": "A", "authors": "A", "year": 2026, "url": "http://example.org/a"}]}
        with self.assertRaises(IndexValidationError):
            validate_index(doc)


class IndexRenderTests(unittest.TestCase):
    def test_year_descending(self):
        html = render_index(validate_index(TWO))
        self.assertLess(html.index("Alpha"), html.index("Beta"))
        self.assertIn('class="ledger"', html)
        self.assertNotIn("citation_", html)
        self.assertIn("Systems Engineering, Loughborough University: papers", html)
        self.assertIn("https://systems-researcher.github.io/research-programme/", html)

    def test_empty_list_is_valid(self):
        html = render_index(validate_index({"papers": []}))
        self.assertIn("no papers are registered yet", html)


if __name__ == "__main__":
    unittest.main()
