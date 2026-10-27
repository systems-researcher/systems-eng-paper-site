"""Head tags from one validated paper. Empty values are omitted."""

import re

from render.dates import iso_date, scholar_date

_ARXIV = re.compile(r"(?:arXiv:)?(\d{4}\.\d{4,5})(?:v\d+)?$", re.I)
_DOI_URL = "https://doi.org/"


def canonical_url(paper, repository):
    site = (paper.get("links") or {}).get("site")
    if site and str(site).strip():
        return str(site).strip()
    owner, repo = repository.split("/", 1)
    return "https://%s.github.io/%s/" % (owner, repo)


def bare_doi(value):
    text = str(value).strip()
    if text.startswith(_DOI_URL):
        return text[len(_DOI_URL):]
    return text


def arxiv_url(value):
    text = str(value).strip()
    if text.startswith("https://") or text.startswith("http://"):
        return text
    match = _ARXIV.search(text)
    if not match:
        raise ValueError("arxiv is not a URL or arXiv id")
    return "https://arxiv.org/abs/%s" % match.group(1)


def citation_pdf_url(paper, canonical):
    pdf = (paper.get("links") or {}).get("pdf")
    if not pdf or not str(pdf).strip():
        return None
    text = str(pdf).strip()
    if text.startswith("https://") or text.startswith("http://"):
        return None
    base = canonical if canonical.endswith("/") else canonical + "/"
    return base + text.lstrip("./")


def _add(tags, kind, key, content):
    if content is None:
        return
    text = str(content).strip()
    if text:
        tags.append((kind, key, text))


def meta_tags(paper, canonical):
    tags = []
    description = paper.get("description") or paper["abstract"]
    if not paper.get("description") and len(description) > 300:
        description = description[:299].rstrip() + "..."
    _add(tags, "name", "description", description)
    _add(tags, "property", "og:type", "article")
    _add(tags, "property", "og:title", paper["title"])
    _add(tags, "property", "og:description", description)
    _add(tags, "property", "og:url", canonical)
    _add(tags, "name", "twitter:card", "summary_large_image")
    _add(tags, "name", "twitter:title", paper["title"])
    _add(tags, "name", "twitter:description", description)
    _add(tags, "name", "DC.title", paper["title"])
    for author in paper["authors"]:
        _add(tags, "name", "DC.creator", author["name"])
    _add(tags, "name", "DC.publisher", paper.get("publisher") or "Loughborough University")
    published = paper.get("published") or str(paper["year"])
    _add(tags, "name", "DC.date", iso_date(published))
    _add(tags, "name", "DC.type", paper.get("type") or _dc_type(paper))
    links = paper.get("links") or {}
    doi = links.get("doi")
    _add(tags, "name", "DC.identifier", (_DOI_URL + bare_doi(doi)) if doi else canonical)
    _add(tags, "name", "DC.rights", paper["licence"])
    for rel in ("arxiv", "code", "pdf"):
        if paper.get("links", {}).get(rel):
            _add(tags, "name", "DC.relation", str(paper["links"][rel]))  # identifier is DOI-or-canonical, never these
    _add(tags, "name", "citation_title", paper["title"])
    for author in paper["authors"]:
        _add(tags, "name", "citation_author", author["name"])
    _add(tags, "name", "citation_publication_date", scholar_date(published))
    if paper.get("online"):
        _add(tags, "name", "citation_online_date", scholar_date(paper["online"]))
    venue = paper.get("venue")
    kind = paper.get("venue_kind") or "journal"
    if venue and kind == "conference":
        _add(tags, "name", "citation_conference_title", venue)
    elif venue and kind == "journal":
        _add(tags, "name", "citation_journal_title", venue)
    if doi:
        _add(tags, "name", "citation_doi", bare_doi(doi))
    pdf = citation_pdf_url(paper, canonical)
    _add(tags, "name", "citation_pdf_url", pdf)
    return tags


def _dc_type(paper):
    kind = paper.get("venue_kind") or "journal"
    if kind == "software":
        return "Software"
    return "Text"
