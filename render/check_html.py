"""Assert rendered HTML stays on-origin and correctly labelled. No fetching."""

import argparse
import sys
from html.parser import HTMLParser
from pathlib import Path

BANNED_HOSTS = ("fonts.googleapis.com", "fonts.gstatic.com", "cdn.jsdelivr.net", "unpkg.com")
CITATION_NAMES = ("citation_title", "citation_author", "citation_publication_date")


def _attrs_dict(attrs):
    out = {}
    for k, v in attrs:
        if k not in out:
            out[k] = v or ""
    return out


class _Scanner(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.h1 = 0
        self.skip_link = False
        self.main_main = False
        self.meta = {}
        self.stylesheets = []
        self.urls = []  # (kind, value)
        self.citation = False

    def handle_starttag(self, tag, attrs):
        a = _attrs_dict(attrs)
        if tag == "h1":
            self.h1 += 1
        elif tag == "main" and a.get("id") == "main":
            self.main_main = True
        elif tag == "a":
            classes = a.get("class", "").split()
            if "skip" in classes and a.get("href") == "#main":
                self.skip_link = True
            href = a.get("href")
            if href is not None:
                self.urls.append(("a href", href))
        elif tag == "meta":
            name = a.get("name") or a.get("property")
            if name:
                self.meta[name] = a.get("content", "")
                if a.get("name") in CITATION_NAMES:
                    self.citation = True
        elif tag == "link":
            rels = a.get("rel", "").split()
            href = a.get("href")
            if href is not None:
                if "stylesheet" in rels:
                    self.stylesheets.append(href)
                    self.urls.append(("stylesheet href", href))
                elif rels:
                    self.urls.append(("link href rel=%s" % rels[0], href))
                else:
                    self.urls.append(("link href", href))
        elif tag == "script":
            src = a.get("src")
            if src is not None:
                self.urls.append(("script src", src))
        elif tag in ("img", "figure"):
            src = a.get("src")
            if src is not None:
                self.urls.append(("%s src" % tag, src))


def check(html, index=False, css_texts=None):
    problems = []
    scanner = _Scanner()
    scanner.feed(html)

    if scanner.h1 != 1:
        problems.append("expected exactly one <h1>, found %d" % scanner.h1)
    if not scanner.skip_link:
        problems.append('missing skip link <a class="skip" href="#main">')
    if not scanner.main_main:
        problems.append('missing <main id="main">')
    if scanner.meta.get("color-scheme") != "light dark":
        problems.append('missing <meta name="color-scheme" content="light dark">')
    if not scanner.meta.get("description"):
        problems.append('missing <meta name="description">')
    if not scanner.meta.get("og:title"):
        problems.append('missing <meta property="og:title">')
    if index:
        found = [n for n in CITATION_NAMES if n in scanner.meta]
        if found:
            problems.append("citation tags not allowed on an index page: %s" % ", ".join(found))
    else:
        for name in CITATION_NAMES:
            if name not in scanner.meta:
                problems.append('missing <meta name="%s">' % name)

    for kind, url in scanner.urls:
        for host in BANNED_HOSTS:
            if host in url:
                problems.append("off-origin host %s in %s %r" % (host, kind, url))
        if kind == "a href":
            if url and not url.startswith("#") and not url.startswith("https:"):
                problems.append("outbound anchor must use https:, got %r" % url)
        elif kind in ("stylesheet href", "script src"):
            if "//" in url or ":" in url.split("/")[0]:
                problems.append("%s must be relative, got %r" % (kind, url))
        elif kind == "link href rel=canonical":
            pass  # canonical URLs are absolute by definition; they name this page
        elif url.startswith("http:") or url.startswith("https:") or url.startswith("//"):
            problems.append("%s must not be absolute, got %r" % (kind, url))

    for css in css_texts or []:
        if "url(http" in css.lower():
            problems.append("CSS contains an absolute url(): found url(http")

    return problems


def _linked_css(html_path):
    """Stylesheet texts: --css files plus <link rel="stylesheet"> hrefs resolved
    relative to the HTML file."""
    css_texts = [Path(p).read_text(encoding="utf-8") for p in html_path.css]
    base = html_path.html.parent

    class Links(HTMLParser):
        def __init__(self):
            super().__init__()
            self.hrefs = []

        def handle_starttag(self, tag, attrs):
            a = _attrs_dict(attrs)
            if tag == "link" and "stylesheet" in a.get("rel", "").split():
                self.hrefs.append(a.get("href", ""))

    links = Links()
    links.feed(html_path.html.read_text(encoding="utf-8"))
    texts = []
    for href in links.hrefs:
        path = base / href
        if not path.is_file():
            sys.stderr.write("check_html: missing stylesheet %s\n" % path)
            raise SystemExit(1)
        texts.append(path.read_text(encoding="utf-8"))
    return texts


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m render.check_html")
    parser.add_argument("html", type=Path)
    parser.add_argument("--index", action="store_true")
    parser.add_argument("--css", action="append", default=[])
    args = parser.parse_args(argv)
    css_texts = _linked_css(args)
    problems = check(args.html.read_text(encoding="utf-8"), index=args.index, css_texts=css_texts)
    for p in problems:
        print(p)
    if problems:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
