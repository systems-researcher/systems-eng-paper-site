"""Tests for render.model: YAML loading and paper validation."""
import unittest

from render.model import (
    DuplicateKeyError, PaperError, load_yaml, validate_paper,
)


GOOD = {
    "title": "A title",
    "authors": [{"name": "Gower, Jason"}],
    "year": 2026,
    "licence": "CC-BY-4.0",
    "abstract": "One paragraph.",
}


class LoadTests(unittest.TestCase):
    def test_duplicate_key_raises(self):
        with self.assertRaises(DuplicateKeyError):
            load_yaml("title: a\ntitle: b\n")

    def test_mapping_loads(self):
        self.assertEqual(load_yaml("title: a\n"), {"title": "a"})


class ValidateTests(unittest.TestCase):
    def test_good_returns_mapping(self):
        out = validate_paper(dict(GOOD))
        self.assertEqual(out["title"], "A title")

    def test_missing_required_names_every_field(self):
        with self.assertRaises(PaperError) as cm:
            validate_paper({})
        joined = "\n".join(cm.exception.messages)
        for field in ("title", "authors", "year", "licence", "abstract"):
            self.assertIn(field, joined)

    def test_blank_title(self):
        bad = dict(GOOD, title="   ")
        with self.assertRaises(PaperError) as cm:
            validate_paper(bad)
        self.assertIn("title", "\n".join(cm.exception.messages))

    def test_unknown_top_key(self):
        bad = dict(GOOD, colour="blue")
        with self.assertRaises(PaperError) as cm:
            validate_paper(bad)
        self.assertIn("unknown 'colour'", "\n".join(cm.exception.messages))

    def test_author_requires_name(self):
        bad = dict(GOOD, authors=[{}])
        with self.assertRaises(PaperError) as cm:
            validate_paper(bad)
        self.assertIn("authors[0].name", "\n".join(cm.exception.messages))

    def test_orcid(self):
        bad = dict(GOOD, authors=[{"name": "A", "orcid": "nope"}])
        with self.assertRaises(PaperError):
            validate_paper(bad)
        good = dict(GOOD, authors=[{"name": "Gower, Jason", "orcid": "0000-0002-1825-0097"}])
        self.assertEqual(validate_paper(good)["authors"][0]["orcid"], "0000-0002-1825-0097")

    def test_year_four_digits(self):
        with self.assertRaises(PaperError):
            validate_paper(dict(GOOD, year=26))
        self.assertEqual(validate_paper(dict(GOOD, year="2026"))["year"], 2026)

    def test_abstract_cap(self):
        with self.assertRaises(PaperError):
            validate_paper(dict(GOOD, abstract="x" * 2001))

    def test_description_cap(self):
        with self.assertRaises(PaperError):
            validate_paper(dict(GOOD, description="x" * 301))

    def test_unknown_venue_kind_and_accent(self):
        with self.assertRaises(PaperError):
            validate_paper(dict(GOOD, venue_kind="magazine"))
        with self.assertRaises(PaperError):
            validate_paper(dict(GOOD, accent="#ff0000"))

    def test_language_bcp47(self):
        with self.assertRaises(PaperError):
            validate_paper(dict(GOOD, language="not a tag"))
        self.assertEqual(validate_paper(dict(GOOD, language="en-GB"))["language"], "en-GB")

    def test_unknown_link_key(self):
        with self.assertRaises(PaperError):
            validate_paper(dict(GOOD, links={"homepage": "https://example.com"}))

    def test_section_slug_and_blank_body(self):
        with self.assertRaises(PaperError):
            validate_paper(dict(GOOD, sections=[{"id": "Bad Id", "title": "T", "body": "x"}]))
        with self.assertRaises(PaperError):
            validate_paper(dict(GOOD, sections=[{"id": "ok", "title": "T", "body": "  "}]))
        good = dict(GOOD, sections=[{"id": "intro", "title": "T", "body": "x"}])
        self.assertEqual(validate_paper(good)["sections"][0]["id"], "intro")

    def test_figure_rules(self):
        ok = dict(GOOD, figures=[{
            "id": "arch", "src": "content/figures/arch.svg",
            "alt": "Architecture", "caption": "System architecture.",
        }])
        self.assertEqual(validate_paper(ok)["figures"][0]["id"], "arch")
        bad_src = dict(ok, figures=[dict(ok["figures"][0], src="content/img/a.png")])
        with self.assertRaises(PaperError):
            validate_paper(bad_src)
        bad_alt = dict(ok, figures=[{"id": "b", "src": "content/figures/b.png", "caption": "c"}])
        with self.assertRaises(PaperError):
            validate_paper(bad_alt)

    def test_figure_src_traversal_rejected(self):
        base = {
            "id": "arch", "alt": "A", "caption": "c",
        }
        for src in (
            "content/figures/../../docs/assets/og.png",
            "content/figures/../secret.png",
            "/content/figures/arch.svg",
            "C:/content/figures/arch.svg",
            "content/figures\\arch.svg",
            "content/figures/foo/../../../etc/passwd.png",
        ):
            bad = dict(GOOD, figures=[dict(base, src=src)])
            with self.assertRaises(PaperError) as cm:
                validate_paper(bad)
            joined = "\n".join(cm.exception.messages)
            self.assertIn("figures[0].src must be under content/figures/", joined, src)

    def test_links_null_normalised(self):
        out = validate_paper(dict(GOOD, links=None))
        self.assertEqual(out["links"], {})
        with self.assertRaises(PaperError) as cm:
            validate_paper(dict(GOOD, links=["not", "a", "map"]))
        self.assertIn("links must be mapping", "\n".join(cm.exception.messages))

    def test_figure_after_unknown_section(self):
        bad = dict(GOOD, figures=[{
            "id": "arch", "src": "content/figures/arch.svg",
            "alt": "A", "caption": "c", "after": "missing",
        }])
        with self.assertRaises(PaperError):
            validate_paper(bad)

    def test_arxiv_link_shape(self):
        bad = dict(GOOD, links={"arxiv": "arxiv.org/abs/1234.5678"})
        with self.assertRaises(PaperError):
            validate_paper(bad)
        ok_url = dict(GOOD, links={"arxiv": "https://arxiv.org/abs/2401.12345"})
        self.assertEqual(validate_paper(ok_url)["links"]["arxiv"], "https://arxiv.org/abs/2401.12345")
        ok_tag = dict(GOOD, links={"arxiv": "arXiv:2401.12345"})
        self.assertEqual(validate_paper(ok_tag)["links"]["arxiv"], "arXiv:2401.12345")

    def test_changelog_and_bibtex(self):
        bad_c = dict(GOOD, changelog=[{"date": "", "text": "x"}])
        with self.assertRaises(PaperError):
            validate_paper(bad_c)
        ok_c = dict(GOOD, changelog=[{"date": "2026-01-02", "text": "v2"}])
        self.assertEqual(validate_paper(ok_c)["changelog"], [{"date": "2026-01-02", "text": "v2"}])
        bad_b = dict(GOOD, bibtex_type="book")
        with self.assertRaises(PaperError):
            validate_paper(bad_b)


if __name__ == "__main__":
    unittest.main()
