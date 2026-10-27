"""Index model: validate papers.yml into a normalized index document."""
from render.model import _YEAR
from render.model import _blank


class IndexValidationError(Exception):
    def __init__(self, messages):
        self.messages = messages
        super().__init__("\n".join(self.messages))


KNOWN_TOP = frozenset({"description", "papers"})
KNOWN_ENTRY = frozenset({"title", "authors", "year", "url", "venue"})


def _year(value):
    if isinstance(value, int) and _YEAR.match(str(value)):
        return value
    if isinstance(value, str) and _YEAR.match(value.strip()):
        return int(value.strip())
    return None


def validate_index(doc: object) -> dict:
    if not isinstance(doc, dict):
        raise IndexValidationError(["document must be a mapping"])
    errors = []
    for key in doc:
        if key not in KNOWN_TOP:
            errors.append("unknown '%s'" % key)
    description = doc.get("description")
    if description is not None and not isinstance(description, str):
        errors.append("description must be a string")
        description = None
    papers_in = doc.get("papers")
    if not isinstance(papers_in, list):
        errors.append("missing required field 'papers'")
        papers_in = []
    papers = []
    seen_urls = set()
    for i, entry in enumerate(papers_in):
        path = "papers[%d]" % i
        if not isinstance(entry, dict):
            errors.append("%s must be a mapping" % path)
            continue
        for key in entry:
            if key not in KNOWN_ENTRY:
                errors.append("unknown '%s.%s'" % (path, key))
        if not isinstance(entry.get("title"), str) or _blank(entry["title"]):
            errors.append("missing required field '%s.title'" % path)
        if not isinstance(entry.get("authors"), str) or _blank(entry["authors"]):
            errors.append("missing required field '%s.authors'" % path)
        year_n = _year(entry.get("year"))
        if year_n is None:
            errors.append("missing required field '%s.year'" % path)
        url = entry.get("url")
        if not isinstance(url, str) or _blank(url):
            errors.append("missing required field '%s.url'" % path)
        else:
            url = url.strip()
            if not url.startswith("https://"):
                errors.append("%s.url must start with https://" % path)
            if url in seen_urls:
                errors.append("%s.url duplicate '%s'" % (path, url))
            seen_urls.add(url)
        venue = entry.get("venue")
        if venue is not None and not _blank(venue) and not isinstance(venue, str):
            errors.append("%s.venue must be a string" % path)
        if isinstance(venue, str):
            venue = venue.strip() or None
        else:
            venue = None
        papers.append({
            "title": entry.get("title"),
            "authors": entry.get("authors"),
            "year": year_n,
            "url": url,
            "venue": venue,
        })
    if errors:
        raise IndexValidationError(errors)
    return {"description": description, "papers": papers}
