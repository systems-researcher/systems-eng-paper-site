import html as html_mod
from pathlib import Path

from render.bibtex import render_bibtex
from render.markdown import render_inline, render_markdown
from render.meta import arxiv_url, bare_doi, citation_pdf_url, meta_tags

_LINK_LABELS = (
    ("doi", "DOI"),
    ("pdf", "PDF"),
    ("code", "Code"),
    ("arxiv", "arXiv"),
    ("slides", "Slides"),
    ("poster", "Poster"),
    ("video", "Video"),
)


def _esc(value):
    return html_mod.escape(str(value), quote=True)


def _meta_html(tags, canonical):
    lines = []
    for kind, key, content in tags:
        lines.append('<meta %s="%s" content="%s">' % (kind, _esc(key), _esc(content)))
    lines.append('<link rel="canonical" href="%s">' % _esc(canonical))
    return "\n".join(lines)


def _visible_href(key, value, canonical):
    text = str(value).strip()
    if not text:
        return None
    if key == "doi":
        return "https://doi.org/" + bare_doi(text)
    if key == "arxiv":
        return arxiv_url(text)
    if key == "pdf" and not text.startswith("http"):
        return citation_pdf_url({"links": {"pdf": text}}, canonical)
    return text


def _record(paper):
    custom = paper.get("record")
    if isinstance(custom, dict) and custom:
        rows = [(str(k), str(v)) for k, v in custom.items() if str(v).strip()]
    else:
        rows = []
        if paper.get("venue"):
            rows.append(("Venue", paper["venue"]))
        rows.append(("Year", str(paper["year"])))
        rows.append(("Licence", paper["licence"]))
    body = "".join("<dt>%s</dt><dd>%s</dd>" % (_esc(k), _esc(v)) for k, v in rows)
    return (
        '<aside class="side record" aria-labelledby="h-record">'
        '<p class="record-t" id="h-record">The record</p><dl>%s</dl></aside>' % body
    )


def _figure(fig, public_src):
    no_zoom = fig.get("decorative") or fig.get("zoom") is False
    alt = "" if fig.get("decorative") else fig["alt"]
    attrs = ' class="plate"'
    if fig.get("wide"):
        attrs = ' class="plate is-wide"'
    if no_zoom:
        attrs += " data-no-zoom"
    title = ""
    if fig.get("title"):
        title = '<p class="plate-title">%s</p>' % _esc(fig["title"])
    return (
        '<figure%s><div class="plate-body">%s<img src="%s" alt="%s"></div>'
        '<figcaption id="fig-%s-cap"><span class="fig-n">%s</span> %s</figcaption></figure>'
        % (
            attrs,
            title,
            _esc(public_src),
            _esc(alt),
            _esc(fig["id"]),
            _esc(fig.get("number") or ""),
            render_inline(fig["caption"]),
        )
    )


def render_page(paper, canonical, figure_srcs, docs_root):
    docs_root = Path(docs_root)
    tags = meta_tags(paper, canonical)
    authors = []
    for author in paper["authors"]:
        name = _esc(author["name"])
        if author.get("orcid"):
            name = '<a href="https://orcid.org/%s">%s</a>' % (_esc(author["orcid"]), name)
        line = "<span>%s</span>" % name
        if author.get("affiliation"):
            line += "<span>%s</span>" % _esc(author["affiliation"])
        authors.append(line)
    links = []
    for key, label in _LINK_LABELS:
        value = (paper.get("links") or {}).get(key)
        href = _visible_href(key, value, canonical) if value is not None else None
        if href:
            links.append('<a href="%s">%s</a>' % (_esc(href), label))
    figures = list(paper.get("figures") or [])
    for i, fig in enumerate(figures, 1):
        fig.setdefault("number", "Figure %d" % i)
    by_after = {}
    for fig in figures:
        by_after.setdefault(fig.get("after") or "end", []).append(fig)
    sections = []
    for i, sec in enumerate(paper.get("sections") or [], 1):
        side = ""
        if sec.get("side"):
            side = '<aside class="side"><span class="side-k">%s</span> %s</aside>' % (
                _esc(sec["side"]["label"]),
                _esc(sec["side"]["text"]),
            )
        block = (
            '<section class="sec" id="%s"><h2 id="h-%s"><a class="sec-n" href="#%s">%d</a> %s</h2>%s%s</section>'
            % (
                sec["id"],
                sec["id"],
                sec["id"],
                i,
                _esc(sec["title"]),
                side,
                render_markdown(sec["body"]),
            )
        )
        sections.append(
            block
            + "".join(_figure(f, figure_srcs[f["id"]]) for f in by_after.get(sec["id"], []))
        )
    extras = []
    n = len(paper.get("sections") or [])
    if paper.get("ethics"):
        n += 1
        extras.append(
            '<section class="sec" id="ethics"><h2 id="h-ethics"><a class="sec-n" href="#ethics">%d</a> Ethics</h2>%s</section>'
            % (n, render_markdown(paper["ethics"]))
        )
    if paper.get("funding"):
        n += 1
        extras.append(
            '<section class="sec" id="funding"><h2 id="h-funding"><a class="sec-n" href="#funding">%d</a> Funding</h2>%s</section>'
            % (n, render_markdown(paper["funding"]))
        )
    changelog = ""
    if paper.get("changelog"):
        items = "".join(
            "<li><span>%s</span> %s</li>" % (_esc(c["date"]), _esc(c["text"]))
            for c in paper["changelog"]
        )
        changelog = '<section class="ledger"><h2>Changelog</h2><ul>%s</ul></section>' % items
    subtitle = (
        "<p>%s</p>" % _esc(paper["subtitle"]) if paper.get("subtitle") else ""
    )
    bib = _esc(render_bibtex(paper, canonical))
    opening_figs = "".join(
        _figure(f, figure_srcs[f["id"]]) for f in by_after.get("opening", [])
    )
    end_figs = "".join(
        _figure(f, figure_srcs[f["id"]]) for f in by_after.get("end", [])
    )
    emblem_html = (
        '<img class="emblem" src="assets/emblem.svg" alt="">'
        if (docs_root / "assets" / "emblem.svg").exists()
        else ""
    )
    lang = paper.get("language") or "en"
    accent = paper.get("accent") or "petrol"
    cr = "<!-- Copyright (c) %s %s | SPDX-License-Identifier: %s -->\n" % (
        paper.get("year", ""),
        _esc(paper["authors"][0]["name"]),
        _esc(paper["licence"]),
    )
    return cr + """<!DOCTYPE html>
<html lang="%s" data-accent="%s">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>%s</title>
%s
<link rel="stylesheet" href="assets/tokens.css">
<link rel="stylesheet" href="assets/site.css">
<link rel="icon" href="assets/favicon.ico">
<script src="assets/zoom.js" defer></script>
<script src="assets/cite.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip content</a>
<header class="masthead">
  <div class="masthead-in">
    %s
    <p class="brand-name">Systems Engineering, Loughborough University</p>
    <!-- logo slot: official LU mark when approved -->
    <span class="logo-slot"></span>
  </div>
</header>
<main id="main" class="sheet">
  <header class="opening">
    <h1>%s</h1>
    <p class="byline">%s</p>
    %s
    <p class="lede">%s</p>
    %s
    <p class="links">%s</p>
  </header>
  %s
  %s
  %s
  <section class="sec" id="cite">
    <h2>Cite this</h2>
    <button type="button" data-copy="bibtex">Copy BibTeX</button>
    <pre class="cite" id="bibtex">%s</pre>
  </section>
  %s
</main>
<footer class="colophon">
  <div class="colophon-in">
    <p>Systems Engineering, Loughborough University. %s</p>
    <p><a href="%s">%s</a></p>
    <p><a href="https://systems-researcher.github.io/systems-eng-paper-site/">Department papers</a></p>
  </div>
</footer>
</body>
</html>
""" % (
        _esc(lang),
        _esc(accent),
        _esc(paper["title"]),
        _meta_html(tags, canonical),
        emblem_html,
        _esc(paper["title"]),
        "".join(authors),
        subtitle,
        _esc(paper["abstract"]),
        _record(paper),
        "".join(links),
        opening_figs,
        "".join(sections) + end_figs,
        "".join(extras),
        bib,
        changelog,
        _esc(paper["licence"]),
        _esc(canonical),
        _esc(canonical),
    )
