import re

_NON_ALNUM = re.compile(r"[^a-z0-9]+")

_DEFAULT_TYPE = {
    "journal": "article",
    "conference": "inproceedings",
    "thesis": "phdthesis",
    "report": "techreport",
}


def family_name(name):
    text = name.strip()
    if "," in text:
        return text.split(",", 1)[0].strip()
    return text.split()[-1]


def cite_key(paper):
    explicit = paper.get("cite_key")
    if explicit:
        return str(explicit).strip()
    family = family_name(paper["authors"][0]["name"]).lower()
    slug = _NON_ALNUM.sub("", family)
    return "%s%s" % (slug, paper["year"])


def bibtex_type(paper):
    explicit = paper.get("bibtex_type")
    if explicit:
        return explicit
    return _DEFAULT_TYPE.get(paper.get("venue_kind") or "journal", "misc")


def _bare_doi(value):
    text = str(value).strip()
    prefix = "https://doi.org/"
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def render_bibtex(paper, canonical):
    kind = bibtex_type(paper)
    fields = [
        ("title", paper["title"]),
        ("author", " and ".join(a["name"] for a in paper["authors"])),
        ("year", str(paper["year"])),
    ]
    venue = paper.get("venue")
    if venue and kind == "article":
        fields.append(("journal", venue))
    elif venue and kind == "inproceedings":
        fields.append(("booktitle", venue))
    links = paper.get("links") or {}
    if links.get("doi"):
        fields.append(("doi", _bare_doi(links["doi"])))
    fields.append(("url", canonical))
    body = ",\n  ".join("%s = {%s}" % pair for pair in fields)
    return "@%s{%s,\n  %s\n}\n" % (kind, cite_key(paper), body)
