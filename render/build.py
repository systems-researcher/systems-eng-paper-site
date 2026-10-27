"""Render one paper site. Writes docs/index.html only after validation passes."""

import os
import shutil
import sys
from pathlib import Path

from render.html import render_page
from render.meta import canonical_url
from render.model import DuplicateKeyError, PaperError, format_errors, load_yaml, validate_paper
from render.og import place_og


def build_paper(yaml_path, repo_root, docs_root):
    yaml_path = Path(yaml_path)
    repo_root = Path(repo_root)
    docs_root = Path(docs_root)
    try:
        doc = load_yaml(yaml_path.read_text(encoding="utf-8"))
        paper = validate_paper(doc)
        _check_files(paper, repo_root)
        repository = os.environ.get(
            "GITHUB_REPOSITORY", "systems-researcher/systems-eng-paper-site"
        )
        canonical = canonical_url(paper, repository)
        figure_srcs = _copy_figures(paper, repo_root, docs_root)
        place_og(
            repo_root,
            docs_root / "assets",
            Path(__file__).resolve().parent / "assets" / "og.png",
        )
        html = render_page(paper, canonical, figure_srcs, docs_root)
    except PaperError as exc:
        sys.stderr.write(format_errors("paper.yaml", exc.messages) + "\n")
        raise SystemExit(1)
    except (DuplicateKeyError, ValueError, OSError) as exc:
        sys.stderr.write("paper.yaml: %s\n" % exc)
        raise SystemExit(1)
    docs_root.mkdir(parents=True, exist_ok=True)
    (docs_root / "index.html").write_text(html, encoding="utf-8")


def _check_files(paper, repo_root):
    basenames = []
    figures_root = (repo_root / "content" / "figures").resolve()
    for fig in paper.get("figures") or []:
        src = (repo_root / fig["src"]).resolve()
        if not src.is_relative_to(figures_root):
            sys.stderr.write(
                "paper.yaml: figure path escapes content/figures/ '%s'\n"
                % fig["src"]
            )
            raise SystemExit(1)
        if not src.is_file():
            sys.stderr.write("paper.yaml: missing figure file '%s'\n" % fig["src"])
            raise SystemExit(1)
        if src.name in basenames:
            sys.stderr.write(
                "paper.yaml: duplicate figure basename '%s'\n" % src.name
            )
            raise SystemExit(1)
        basenames.append(src.name)
    pdf = (paper.get("links") or {}).get("pdf")
    if pdf and not str(pdf).startswith("http"):
        if "/" in str(pdf):
            sys.stderr.write(
                "paper.yaml: links.pdf relative path must be a bare filename "
                "in docs/, beside index.html\n"
            )
            raise SystemExit(1)
        if not (repo_root / "docs" / str(pdf)).is_file():
            sys.stderr.write("paper.yaml: missing pdf '%s'\n" % pdf)
            raise SystemExit(1)


def _copy_figures(paper, repo_root, docs_root):
    dest = docs_root / "assets" / "figures"
    dest.mkdir(parents=True, exist_ok=True)
    figures_root = (repo_root / "content" / "figures").resolve()
    out = {}
    for fig in paper.get("figures") or []:
        src = (repo_root / fig["src"]).resolve()
        if not src.is_relative_to(figures_root):
            raise ValueError("figure path escapes content/figures/: %s" % fig["src"])
        shutil.copyfile(src, dest / src.name)
        out[fig["id"]] = "assets/figures/%s" % src.name
    return out


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    build_paper(root / "content" / "paper.yaml", root, root / "docs")
