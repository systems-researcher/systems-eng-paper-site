"""Render the department index. Writes docs/index.html only after validation passes."""

import shutil
import sys
from pathlib import Path

from render.index_html import render_index
from render.index_model import IndexValidationError, validate_index
from render.model import DuplicateKeyError, PaperError, format_errors, load_yaml


def build_index(yaml_path, repo_root, docs_root):
    yaml_path = Path(yaml_path)
    repo_root = Path(repo_root)
    docs_root = Path(docs_root)
    try:
        doc = load_yaml(yaml_path.read_text(encoding="utf-8"))
        index = validate_index(doc)
        dest = docs_root / "assets" / "og.png"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(repo_root / "render" / "assets" / "og.png", dest)
        html = render_index(index)
    except (IndexValidationError, PaperError) as exc:
        sys.stderr.write(format_errors("papers.yml", exc.messages) + "\n")
        raise SystemExit(1)
    except (DuplicateKeyError, ValueError, OSError) as exc:
        sys.stderr.write("papers.yml: %s\n" % exc)
        raise SystemExit(1)
    docs_root.mkdir(parents=True, exist_ok=True)
    (docs_root / "index.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    build_index(root / "papers.yml", root, root / "docs")
