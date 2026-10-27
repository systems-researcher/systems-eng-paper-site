import unittest
from render.bibtex import bibtex_type, cite_key, family_name, render_bibtex
from render.dates import iso_date, scholar_date


class NameTests(unittest.TestCase):
    def test_family_before_comma(self):
        self.assertEqual(family_name("Gower, Jason D."), "Gower")

    def test_family_last_token(self):
        self.assertEqual(family_name("Jason Gower"), "Gower")

    def test_cite_key_strips_non_alnum(self):
        paper = {"authors": [{"name": "O'Neil, Pat"}], "year": 2026}
        self.assertEqual(cite_key(paper), "oneil2026")

    def test_explicit_cite_key_wins(self):
        paper = {"authors": [{"name": "Gower, Jason"}], "year": 2026, "cite_key": "gower-probe"}
        self.assertEqual(cite_key(paper), "gower-probe")


class TypeTests(unittest.TestCase):
    def test_defaults(self):
        self.assertEqual(bibtex_type({"venue_kind": "journal"}), "article")
        self.assertEqual(bibtex_type({"venue_kind": "conference"}), "inproceedings")
        self.assertEqual(bibtex_type({"venue_kind": "thesis"}), "phdthesis")
        self.assertEqual(bibtex_type({"venue_kind": "report"}), "techreport")
        self.assertEqual(bibtex_type({"venue_kind": "software"}), "misc")

    def test_explicit_wins(self):
        self.assertEqual(
            bibtex_type({"venue_kind": "journal", "bibtex_type": "misc"}), "misc"
        )


class RenderTests(unittest.TestCase):
    def test_omits_empty_optional_fields(self):
        paper = {
            "title": "T",
            "authors": [{"name": "Gower, Jason"}, {"name": "Ji, Siyuan"}],
            "year": 2026,
            "venue_kind": "software",
        }
        text = render_bibtex(paper, "https://example.github.io/paper/")
        self.assertIn("@misc{gower2026,", text)
        self.assertIn("author = {Gower, Jason and Ji, Siyuan}", text)
        self.assertNotIn("journal", text)
        self.assertNotIn("doi", text)
        self.assertIn("url = {https://example.github.io/paper/}", text)

    def test_article_has_journal(self):
        paper = {
            "title": "T",
            "authors": [{"name": "Gower, Jason"}],
            "year": 2026,
            "venue_kind": "journal",
            "venue": "Systems",
            "links": {"doi": "10.1000/xyz"},
        }
        text = render_bibtex(paper, "https://example.github.io/paper/")
        self.assertIn("@article{", text)
        self.assertIn("journal = {Systems}", text)
        self.assertIn("doi = {10.1000/xyz}", text)


class DateTests(unittest.TestCase):
    def test_scholar_strips_leading_zeros(self):
        self.assertEqual(scholar_date("1996-05-17"), "1996/5/17")
        self.assertEqual(scholar_date("2026"), "2026")

    def test_iso_passthrough(self):
        self.assertEqual(iso_date("2026-05-17"), "2026-05-17")
        self.assertEqual(iso_date("2026"), "2026")


if __name__ == "__main__":
    unittest.main()
