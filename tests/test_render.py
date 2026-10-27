import os
import shutil
import tempfile
import unittest
from pathlib import Path

from render.build import _check_files, build_paper
from render.og import png_size

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "paper.yaml"


class PngTests(unittest.TestCase):
    def test_ihdr(self):
        self.assertEqual(png_size(ROOT / "render" / "assets" / "og.png"), (1200, 630))


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        content = self.tmp / "content"
        shutil.copytree(ROOT / "tests" / "fixtures", content)
        # fixture paths say content/figures/...; the copy already sits at content/
        self.docs = self.tmp / "docs"
        self.docs.mkdir()
        (self.docs / "index.html").write_text("STUB", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_fixture_renders_required_marks(self):
        os.environ["GITHUB_REPOSITORY"] = "systems-researcher/example-paper"
        build_paper(self.tmp / "content" / "paper.yaml", self.tmp, self.docs)
        html = (self.docs / "index.html").read_text(encoding="utf-8")
        self.assertIn("Epistemic adequacy under pressure", html)
        self.assertIn("Gower, Jason", html)
        self.assertIn("Ji, Siyuan", html)
        self.assertIn("CC-BY-4.0", html)
        self.assertIn('id="bibtex"', html)
        self.assertIn("citation_title", html)
        self.assertIn("citation_author", html)
        self.assertIn("citation_publication_date", html)
        self.assertIn("DC.title", html)
        self.assertIn("og:title", html)
        self.assertIn('name="twitter:card"', html)
        self.assertIn('class="skip"', html)
        self.assertIn('href="#main"', html)
        self.assertIn('<main id="main"', html)
        self.assertIn('name="color-scheme" content="light dark"', html)
        self.assertIn("figure.plate".replace("figure.plate", 'class="plate"'), html)
        self.assertIn("plate-body", html)
        self.assertIn("fig-n", html)
        self.assertIn("logo slot: official LU mark when approved", html)
        for banned in ("fonts.googleapis.com", "fonts.gstatic.com", "cdn.jsdelivr.net", "unpkg.com"):
            self.assertNotIn(banned, html)
        self.assertIn('href="https://orcid.org/0000-0002-1825-0097"', html)
        self.assertIn("https://arxiv.org/abs/2401.00001", html)
        self.assertIn("data-no-zoom", html)
        self.assertEqual(html.count('property="og:image"'), 1)
        self.assertEqual(html.count('name="twitter:image"'), 1)

    def test_missing_title_does_not_replace_index(self):
        path = self.tmp / "content" / "paper.yaml"
        text = path.read_text(encoding="utf-8").replace('title: "Epistemic adequacy under pressure"\n', "")
        path.write_text(text, encoding="utf-8")
        with self.assertRaises(SystemExit):
            build_paper(path, self.tmp, self.docs)
        self.assertEqual((self.docs / "index.html").read_text(encoding="utf-8"), "STUB")

    def test_blank_link_emits_no_empty_anchor(self):
        path = self.tmp / "content" / "paper.yaml"
        text = path.read_text(encoding="utf-8").replace('slides: "https://example.org/slides"', 'slides: ""')
        path.write_text(text, encoding="utf-8")
        os.environ["GITHUB_REPOSITORY"] = "systems-researcher/example-paper"
        build_paper(path, self.tmp, self.docs)
        html = (self.docs / "index.html").read_text(encoding="utf-8")
        self.assertNotIn('href=""', html)

    def test_links_null_builds(self):
        path = self.tmp / "content" / "paper.yaml"
        text = path.read_text(encoding="utf-8")
        # replace the links block with a null mapping
        start = text.index("\nlinks:")
        end = text.index("\nsections:")
        path.write_text(text[:start] + "\nlinks:\n" + text[end:], encoding="utf-8")
        os.environ["GITHUB_REPOSITORY"] = "systems-researcher/example-paper"
        build_paper(path, self.tmp, self.docs)
        html = (self.docs / "index.html").read_text(encoding="utf-8")
        self.assertIn("Epistemic adequacy under pressure", html)

    def test_check_files_rejects_path_escape(self):
        # lexical escape: src joins outside content/figures after resolve
        outside = self.tmp / "docs" / "assets"
        outside.mkdir(parents=True, exist_ok=True)
        target = outside / "og.png"
        target.write_bytes(b"\x89PNG\r\n\x1a\n")
        paper = {
            "figures": [{
                "id": "x",
                "src": "content/figures/../../docs/assets/og.png",
                "alt": "a",
                "caption": "c",
            }],
        }
        with self.assertRaises(SystemExit):
            _check_files(paper, self.tmp)
        # symlink escape when platform supports it
        fig_dir = self.tmp / "content" / "figures"
        fig_dir.mkdir(parents=True, exist_ok=True)
        link = fig_dir / "escape.png"
        try:
            if link.exists() or link.is_symlink():
                link.unlink()
            link.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        paper2 = {
            "figures": [{
                "id": "y",
                "src": "content/figures/escape.png",
                "alt": "a",
                "caption": "c",
            }],
        }
        with self.assertRaises(SystemExit):
            _check_files(paper2, self.tmp)


if __name__ == "__main__":
    unittest.main()
