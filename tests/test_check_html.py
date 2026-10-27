import unittest
from render.check_html import check

GOOD = """<!DOCTYPE html><html lang="en"><head>
<meta name="color-scheme" content="light dark">
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


if __name__ == "__main__":
    unittest.main()
