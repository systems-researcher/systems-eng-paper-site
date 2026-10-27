"""Department index page: paper masthead, ledger of papers, colophon."""
import html as html_mod

INDEX_TITLE = "Systems Engineering, Loughborough University: papers"
INDEX_URL = "https://systems-researcher.github.io/systems-eng-paper-site/"
RELATED_URL = "https://systems-researcher.github.io/research-programme/"
DEFAULT_DESCRIPTION = (
    "Companion sites papers Systems Engineering, Loughborough University."
)


def _esc(value):
    return html_mod.escape(str(value), quote=True)


def _meta(kind, key, content):
    return '<meta %s="%s" content="%s">' % (kind, _esc(key), _esc(content))


def _item(paper):
    note = _esc(paper["authors"])
    if paper.get("venue"):
        note += ". " + _esc(paper["venue"])
    return (
        '<li><span class="ledger-id">%s</span>'
        '<span><a class="ledger-name" href="%s">%s</a>'
        '<span class="ledger-note">%s</span></span></li>'
        % (paper["year"], _esc(paper["url"]), _esc(paper["title"]), note)
    )


def render_index(index: dict) -> str:
    papers = sorted(index["papers"], key=lambda p: (-p["year"], p["title"]))
    body = (
        '<ul class="ledger">\n%s\n</ul>' % "\n".join(_item(p) for p in papers)
        if papers
        else "<p>no papers are registered yet</p>"
    )
    description = index.get("description") or DEFAULT_DESCRIPTION
    head = "\n".join([
        _meta("property", "og:title", INDEX_TITLE),
        _meta("property", "og:description", description),
        _meta("property", "og:url", INDEX_URL),
        _meta("property", "og:image", INDEX_URL + "assets/og.png"),
        _meta("name", "DC.title", INDEX_TITLE),
        _meta("name", "DC.publisher", "Loughborough University"),
    ])
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>%s</title>
%s
<link rel="stylesheet" href="assets/tokens.css">
<link rel="stylesheet" href="assets/site.css">
</head>
<body>
<a class="skip" href="#main">Skip content</a>
<header class="masthead">
  <div class="masthead-in">
    <img class="emblem" src="assets/emblem.svg" alt="">
    <p class="brand-name">Systems Engineering, Loughborough University</p>
    <!-- logo slot: official LU mark when approved -->
    <span class="logo-slot"></span>
  </div>
</header>
<main id="main" class="sheet">
  <header class="opening">
    <h1>%s</h1>
  </header>
  %s
</main>
<footer class="colophon">
  <div class="colophon-in">
    <p>Systems Engineering, Loughborough University.</p>
    <p>Related: <a href="%s">Systems Researcher research programme</a>.</p>
  </div>
</footer>
</body>
</html>
""" % (
        _esc(INDEX_TITLE),
        head,
        _esc(INDEX_TITLE),
        body,
        _esc(RELATED_URL),
    )
