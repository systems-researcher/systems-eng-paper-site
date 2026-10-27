"""Paper model: YAML loading with duplicate-key detection and PyYAML."""
import re

from yaml import SafeLoader
from yaml import YAMLError
from yaml import load as yaml_load


class DuplicateKeyError(ValueError):
    pass


class PaperError(Exception):
    def __init__(self, messages):
        self.messages = messages
        super().__init__("\n".join(self.messages))


class _UniqueLoader(SafeLoader):
    pass


def _no_dupes(loader, node):
    seen = {}
    for key, value in loader.construct_pairs(node):
        if key in seen:
            raise DuplicateKeyError("duplicate mapping key '%s'" % (key,))
        seen[key] = value
    return seen


_UniqueLoader.add_constructor(
    "tag:yaml.org,2002:map",
    _no_dupes,
)


def load_yaml(text: str) -> object:
    try:
        return yaml_load(text, Loader=_UniqueLoader)
    except YAMLError as exc:
        raise PaperError(["YAML parse error: %s" % exc])


def format_errors(prefix: str, messages: list) -> str:
    return "\n".join("%s: %s" % (prefix, m) for m in messages)


KNOWN_TOP = frozenset({
    "title", "authors", "year", "licence", "abstract",
    "subtitle", "venue", "venue_kind", "published", "online",
    "publisher", "type", "funding", "ethics", "accent", "language",
    "description", "links", "sections", "figures", "record",
    "changelog", "cite_key", "bibtex_type",
})
KNOWN_LINKS = frozenset({
    "doi", "arxiv", "pdf", "code", "slides", "poster", "video", "site",
})
VENUE_KINDS = frozenset({
    "journal", "conference", "thesis", "report", "preprint", "software",
})
ACCENT_KEYS = frozenset({"petrol"})  # style pass may add keys; unknown still fails
BIBTEX_TYPES = frozenset({
    "article", "inproceedings", "phdthesis", "mastersthesis",
    "techreport", "misc",
})
_RESERVED_SECTION_IDS = frozenset({"cite", "ethics", "funding"})
_SLUG = re.compile(r"^[a-z0-9-]+$")
_ORCID = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")  # ORCID group structure, last char digit or X
_BCP47 = re.compile(r"^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$")
_YEAR = re.compile(r"^\d{4}$")
_DATE = re.compile(r"^\d{4}(?:-\d{2}-\d{2})?$")


def _blank(value):
    return value is None or (isinstance(value, str) and value.strip() == "")


def _req_str(doc, key, errors):
    if key not in doc or _blank(doc.get(key)):
        errors.append("missing required field '%s'" % key)
        return
    if not isinstance(doc[key], str):
        errors.append("missing required field '%s'" % key)


def validate_paper(doc: object) -> dict:
    if not isinstance(doc, dict):
        raise PaperError(["document must be a mapping"])
    errors = []
    for key in doc:
        if key not in KNOWN_TOP:
            errors.append("unknown '%s'" % key)
    _req_str(doc, "title", errors)
    _req_str(doc, "licence", errors)
    _req_str(doc, "abstract", errors)
    if "abstract" in doc and len(str(doc["abstract"])) > 2000:
        errors.append("abstract exceeds 2000 characters")
    authors = doc.get("authors")
    clean_authors = []
    year_n = None
    if not isinstance(authors, list) or len(authors) < 1:
        errors.append("missing required field 'authors'")
    else:
        for i, author in enumerate(authors):
            if not isinstance(author, dict) or _blank(author.get("name")):
                errors.append("missing required field 'authors[%d].name'" % i)
                continue
            item = dict(author)
            orcid = item.get("orcid")
            if orcid is not None and not _blank(orcid) and not _ORCID.match(str(orcid)):
                errors.append("authors[%d].orcid not ORCID" % i)
            clean_authors.append(item)
    year = doc.get("year")
    if isinstance(year, int) and _YEAR.match(str(year)):
        year_n = year
    elif isinstance(year, str) and _YEAR.match(year.strip()):
        year_n = int(year.strip())
    else:
        errors.append("missing required field 'year'")
    if "description" in doc and not _blank(doc["description"]):
        if len(str(doc["description"])) > 300:
            errors.append("description exceeds 300 characters")
    if "venue_kind" in doc and not _blank(doc["venue_kind"]):
        if doc["venue_kind"] not in VENUE_KINDS:
            errors.append("unknown venue_kind '%s'" % doc["venue_kind"])
    if "accent" in doc and not _blank(doc["accent"]):
        if doc["accent"] not in ACCENT_KEYS:
            errors.append("unknown accent '%s'" % doc["accent"])
    if "language" in doc and not _blank(doc["language"]):
        if not _BCP47.match(str(doc["language"]).strip()):
            errors.append("language is not a BCP 47 tag")
    if "published" in doc and not _blank(doc["published"]):
        if not _DATE.match(str(doc["published"]).strip()):
            errors.append("published not YYYY or YYYY-MM-DD")
    if "online" in doc and not _blank(doc["online"]):
        if not _DATE.match(str(doc["online"]).strip()):
            errors.append("online is not YYYY or YYYY-MM-DD")
    links = doc.get("links") or {}
    if links and not isinstance(links, dict):
        errors.append("links must be mapping")
        links = {}
    for key in links:
        if key not in KNOWN_LINKS:
            errors.append("unknown key 'links.%s'" % key)
    ids = []
    for i, sec in enumerate(doc.get("sections") or []):
        path = "sections[%d]" % i
        if not isinstance(sec, dict):
            errors.append("%s must be a mapping" % path)
            continue
        sid = sec.get("id")
        if not isinstance(sid, str) or not _SLUG.match(sid):
            errors.append("%s.id must be a slug" % path)
        elif sid in _RESERVED_SECTION_IDS:
            errors.append("%s.id is reserved" % path)
        elif sid in ids:
            errors.append("%s.id duplicate '%s'" % (path, sid))
        else:
            ids.append(sid)
        if _blank(sec.get("title")):
            errors.append("missing required field '%s.title'" % path)
        if _blank(sec.get("body")):
            errors.append("missing required field '%s.body'" % path)
        if sec.get("side") is not None:
            side = sec["side"]
            if not isinstance(side, dict) or _blank(side.get("label")) or _blank(side.get("text")):
                errors.append("%s.side must be mapping with non-blank label and text" % path)
    seen_fig_ids = set()
    for i, fig in enumerate(doc.get("figures") or []):
        path = "figures[%d]" % i
        if not isinstance(fig, dict):
            errors.append("%s must be a mapping" % path)
            continue
        if not isinstance(fig.get("id"), str) or not _SLUG.match(fig["id"]):
            errors.append("%s.id must be slug" % path)
        if fig.get("id") in seen_fig_ids:
            errors.append("%s.id duplicate '%s'" % (path, fig.get("id")))
        seen_fig_ids.add(fig.get("id"))
        src_s = str(fig.get("src") or "")
        if (
            "\\" in src_s
            or src_s.startswith("/")
            or (len(src_s) >= 2 and src_s[1] == ":")
            or any(part == ".." for part in src_s.split("/"))
            or not src_s.startswith("content/figures/")
        ):
            errors.append("%s.src must be under content/figures/" % path)
        suffix = src_s.rsplit(".", 1)[-1].lower()
        if suffix not in ("svg", "png", "jpg", "jpeg", "webp"):
            errors.append("%s.src suffix not allowed" % path)
        if not fig.get("decorative") and _blank(fig.get("alt")):
            errors.append("missing required field '%s.alt'" % path)
        if _blank(fig.get("caption")):
            errors.append("missing required field '%s.caption'" % path)
        after = fig.get("after")
        if after not in (None, "opening") and after not in ids:
            errors.append("%s.after unknown section '%s'" % (path, after))
    _ax = links.get("arxiv")
    if _ax and not (str(_ax).startswith("https://arxiv.org/abs/") or re.match(r"^arXiv:\d{4}\.\d{4,5}$", str(_ax))):
        errors.append("links.arxiv must be an https://arxiv.org/abs/ URL or arXiv:NNNN.NNNNN")
    for i, c in enumerate(doc.get("changelog") or []):
        if not isinstance(c, dict) or _blank(c.get("date")) or _blank(c.get("text")):
            errors.append("changelog[%d] must map non-blank date and text" % i)
    if "bibtex_type" in doc and not _blank(doc["bibtex_type"]) and doc["bibtex_type"] not in BIBTEX_TYPES:
        errors.append("unknown bibtex_type '%s'" % doc["bibtex_type"])
    if errors:
        raise PaperError(errors)
    out = dict(doc)
    out["year"] = year_n
    out["authors"] = clean_authors
    out["links"] = links if isinstance(links, dict) else {}
    return out
