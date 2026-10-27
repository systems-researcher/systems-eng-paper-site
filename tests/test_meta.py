import unittest
from render.meta import (
    arxiv_url, bare_doi, canonical_url, citation_pdf_url, meta_tags,
)

PAPER = {
    "title": "Probe",
    "authors": [{"name": "Gower, Jason"}, {"name": "Ji, Siyuan"}],
    "year": 2026,
    "licence": "CC-BY-4.0",
    "abstract": "A short abstract.",
    "venue_kind": "journal",
    "language": "en",
}


class UrlTests(unittest.TestCase):
    def test_canonical_from_repository(self):
        self.assertEqual(
            canonical_url(PAPER, "systems-researcher/probe"),
            "https://systems-researcher.github.io/probe/",
        )

    def test_canonical_override(self):
        paper = dict(PAPER, links={"site": "https://example.edu/paper"})
        self.assertEqual(canonical_url(paper, "o/r"), "https://example.edu/paper")

    def test_doi_bare(self):
        self.assertEqual(bare_doi("https://doi.org/10.1000/xyz"), "10.1000/xyz")
        self.assertEqual(bare_doi("10.1000/xyz"), "10.1000/xyz")

    def test_arxiv_normalise(self):
        self.assertEqual(arxiv_url("arXiv:2401.00001"), "https://arxiv.org/abs/2401.00001")
        self.assertEqual(arxiv_url("https://arxiv.org/abs/2401.00001"), "https://arxiv.org/abs/2401.00001")

    def test_pdf_relative_becomes_absolute(self):
        paper = dict(PAPER, links={"pdf": "paper.pdf"})
        url = citation_pdf_url(paper, "https://systems-researcher.github.io/probe/")
        self.assertEqual(url, "https://systems-researcher.github.io/probe/paper.pdf")

    def test_pdf_external_is_none(self):
        paper = dict(PAPER, links={"pdf": "https://example.edu/p.pdf"})
        self.assertIsNone(citation_pdf_url(paper, "https://systems-researcher.github.io/probe/"))


class TagTests(unittest.TestCase):
    def test_required_scholar_and_dc(self):
        tags = meta_tags(PAPER, "https://systems-researcher.github.io/probe/")
        names = [t[1] for t in tags]
        self.assertIn("citation_title", names)
        self.assertGreaterEqual(names.count("citation_author"), 1)
        self.assertIn("citation_publication_date", names)
        self.assertIn("DC.title", names)
        self.assertIn("og:title", names)
        self.assertIn("twitter:card", names)
        date = [t[2] for t in tags if t[1] == "citation_publication_date"][0]
        self.assertEqual(date, "2026")

    def test_blank_link_emits_no_tag(self):
        paper = dict(PAPER, links={"doi": "", "code": None})
        tags = meta_tags(paper, "https://systems-researcher.github.io/probe/")
        self.assertFalse(any(t[1] == "citation_doi" for t in tags))
        self.assertTrue(all(t[2].strip() for t in tags))

    def test_conference_uses_conference_title(self):
        paper = dict(PAPER, venue_kind="conference", venue="MODELS")
        tags = meta_tags(paper, "https://systems-researcher.github.io/probe/")
        self.assertTrue(any(t[1] == "citation_conference_title" for t in tags))
        self.assertFalse(any(t[1] == "citation_journal_title" for t in tags))

    def test_software_emits_no_venue_tag(self):
        paper = dict(PAPER, venue_kind="software", venue="GitHub")
        tags = meta_tags(paper, "https://systems-researcher.github.io/probe/")
        self.assertFalse(any(t[1].startswith("citation_") and t[1].endswith("_title") and t[1] != "citation_title" for t in tags))


    def test_og_image_emitted(self):
        tags = meta_tags(PAPER, "https://systems-researcher.github.io/probe/")
        got = dict((t[1], t[2]) for t in tags)
        self.assertEqual(got["og:image"], "https://systems-researcher.github.io/probe/assets/og.png")
        self.assertEqual(got["og:image:width"], "1200")
        self.assertEqual(got["og:image:height"], "630")
        self.assertEqual(got["twitter:image"], "https://systems-researcher.github.io/probe/assets/og.png")

    def test_og_image_slash_normalised_on_site_override(self):
        paper = dict(PAPER, links={"site": "https://example.edu/paper"})
        tags = meta_tags(paper, canonical_url(paper, "o/r"))
        image = [t[2] for t in tags if t[1] == "og:image"][0]
        self.assertEqual(image, "https://example.edu/paper/assets/og.png")

    def test_dc_relation_arxiv_normalised(self):
        paper = dict(PAPER, links={"arxiv": "arXiv:2401.00001"})
        tags = meta_tags(paper, "https://systems-researcher.github.io/probe/")
        self.assertIn(("name", "DC.relation", "https://arxiv.org/abs/2401.00001"), tags)

    def test_dc_relation_arxiv_url_passthrough(self):
        paper = dict(PAPER, links={"arxiv": "https://arxiv.org/abs/2401.00001"})
        tags = meta_tags(paper, "https://systems-researcher.github.io/probe/")
        self.assertIn(("name", "DC.relation", "https://arxiv.org/abs/2401.00001"), tags)


if __name__ == "__main__":
    unittest.main()
