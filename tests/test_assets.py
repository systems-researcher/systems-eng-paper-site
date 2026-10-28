import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets"
FONTS = [
    "instrument-serif-latin-400-normal.woff2",
    "instrument-serif-latin-400-italic.woff2",
    "ibm-plex-sans-latin-400-normal.woff2",
    "ibm-plex-sans-latin-400-italic.woff2",
    "ibm-plex-sans-latin-600-normal.woff2",
    "ibm-plex-mono-latin-400-normal.woff2",
    "InstrumentSerif-OFL.txt",
    "OFL-IBM-Plex-Sans.txt",
]


class AssetTests(unittest.TestCase):
    def test_fonts_present(self):
        for name in FONTS:
            self.assertTrue((ASSETS / "fonts" / name).is_file(), name)

    def test_css_has_no_remote_font(self):
        css = (ASSETS / "site.css").read_text(encoding="utf-8")
        tokens = (ASSETS / "tokens.css").read_text(encoding="utf-8")
        blob = css + tokens
        for banned in ("fonts.googleapis.com", "fonts.gstatic.com", "cdn.jsdelivr.net"):
            self.assertNotIn(banned, blob)
        self.assertIn("instrument-serif-latin-400-normal.woff2", css)
        self.assertIn("ibm-plex-mono-latin-400-normal.woff2", css)
        self.assertIn("--se-plate", tokens)
        self.assertIn("#CD0067", tokens)
        self.assertIn("#330065", blob)
        self.assertNotIn("--sr-", tokens)
        self.assertNotIn("#0F5257", blob)
        self.assertNotIn("EB Garamond", blob)
        self.assertNotIn("eb-garamond", blob)

    def test_zoom_has_no_fetch(self):
        js = (ASSETS / "zoom.js").read_text(encoding="utf-8")
        self.assertNotIn("fetch(", js)
        self.assertIn("figure.plate", js)
        self.assertIn("data-no-zoom", js)
        self.assertIn("HTMLDialogElement", js)


if __name__ == "__main__":
    unittest.main()
