import unittest
from render.markdown import render_inline, render_markdown


class InlineTests(unittest.TestCase):
    def test_escapes_lt(self):
        self.assertNotIn("<script", render_inline("a <script> tag"))
        self.assertIn("&lt;script&gt;", render_inline("a <script> tag"))

    def test_bold_em_code_link(self):
        self.assertIn("<strong>b</strong>", render_inline("**b**"))
        self.assertIn("<em>e</em>", render_inline("*e*"))
        self.assertIn("<code>c</code>", render_inline("`c`"))
        self.assertIn('href="https://example.com"', render_inline("[ex](https://example.com)"))


class BlockTests(unittest.TestCase):
    def test_paragraphs_and_list_and_fence_and_h3(self):
        src = "Para one.\n\nPara two.\n\n- a\n- b\n\n### Head\n\n```\nx < y\n```\n"
        html = render_markdown(src)
        self.assertIn("<p>Para one.</p>", html)
        self.assertIn("<li>a</li>", html)
        self.assertIn("<h3>Head</h3>", html)
        self.assertIn("<pre><code>x &lt; y\n</code></pre>", html)

    def test_unknown_mark_shown_as_text(self):
        html = render_markdown("see ## not a heading\n")
        self.assertIn("## not a heading", html)
        self.assertNotIn("<h2>", html)


if __name__ == "__main__":
    unittest.main()
