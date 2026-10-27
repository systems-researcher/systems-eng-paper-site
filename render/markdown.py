"""Markdown subset. No library. Anything else is escaped text."""

import html
import re

_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
_CODE = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_EM = re.compile(r"\*([^*]+)\*")


def render_inline(text):
    escaped = html.escape(text, quote=True)
    escaped = _CODE.sub(lambda m: "<code>%s</code>" % m.group(1), escaped)
    escaped = _BOLD.sub(lambda m: "<strong>%s</strong>" % m.group(1), escaped)
    escaped = _EM.sub(lambda m: "<em>%s</em>" % m.group(1), escaped)
    escaped = _LINK.sub(
        lambda m: '<a href="%s">%s</a>' % (m.group(2), m.group(1)),
        escaped,
    )
    return escaped


def render_markdown(text):
    lines = text.replace("\r\n", "\n").split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            out.append("<pre><code>%s</code></pre>" % html.escape("\n".join(buf) + "\n", quote=True))
            continue
        if line.startswith("### "):
            out.append("<h3>%s</h3>" % render_inline(line[4:]))
            i += 1
            continue
        if line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append("<li>%s</li>" % render_inline(lines[i][2:]))
                i += 1
            out.append("<ul>%s</ul>" % "".join(items))
            continue
        if line.strip() == "":
            i += 1
            continue
        buf = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(("```", "### ", "- ")):
            buf.append(lines[i])
            i += 1
        out.append("<p>%s</p>" % render_inline(" ".join(buf)))
    return "\n".join(out)
