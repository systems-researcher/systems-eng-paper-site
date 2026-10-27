import unittest
from render.check_html import check

GOOD = """<!DOCTYPE html><html lang="en"><head>
<meta name="color-scheme" content="light dark">
<meta name="description" content="x">
<meta property="og:title" content="y">
<meta name="citation_title" content="T">
<meta name="citation_author" content="A">
<meta name="citation_publication_date" content="2026">
<link rel="stylesheet" href="assets/site.css">
</head><body>
<a class="skip" href="#main">Skip content</a>
<main id="main" class="sheet"><h1>T</h1>
<a href="https://doi.org/10.1000/xyz">DOI</a>
<img src="assets/figures/a.png" alt="a">
</main></body></html>"""


class CheckTests(unittest.TestCase):
    def test_good_is_empty(self):
        self.assertEqual(check(GOOD, index=False), [])

    def test_off_origin_img_fails(self):
        bad = GOOD.replace("assets/figures/a.png", "https://cdn.example/a.png")
        self.assertTrue(check(bad, index=False))

    def test_http_anchor_fails(self):
        bad = GOOD.replace("https://doi.org", "http://doi.org")
        self.assertTrue(any("https" in m for m in check(bad, index=False)))

    def test_missing_required_meta_fails(self):
        bad = GOOD.replace('<meta name="description" content="x">\n', "")
        bad = bad.replace('<meta property="og:title" content="y">\n', "")
        msgs = check(bad, index=False)
        self.assertTrue(any("description" in m for m in msgs))
        self.assertTrue(any("og:title" in m for m in msgs))




class RenderedPagePassesCheck(unittest.TestCase):
    def test_rendered_paper_page_passes_check(self):
        import shutil, tempfile
        from pathlib import Path
        from render.build import build_paper
        from render.check_html import check
        root = Path(__file__).resolve().parents[1]
        tmp = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(root / "tests" / "fixtures", tmp / "content")
            docs = tmp / "docs"
            docs.mkdir()
            (docs / "index.html").write_text("STUB", encoding="utf-8")
            import os
            os.environ["GITHUB_REPOSITORY"] = "systems-researcher/example-paper"
            build_paper(tmp / "content" / "paper.yaml", tmp, docs)
            html = (docs / "index.html").read_text(encoding="utf-8")
            css = (root / "docs" / "assets" / "site.css").read_text(encoding="utf-8")
            self.assertEqual(check(html, css_texts=[css]), [])
        finally:
            shutil.rmtree(tmp)

if __name__ == "__main__":
    unittest.main()
