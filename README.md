# systems-eng-paper-site

Public template for Systems Engineering paper sites, Loughborough University.
This repository's own Pages site is the department index. Colleagues create a
repo from this template, fill in one file, and publish a paper site without
editing HTML.

## 1. Create a repo

Use this template ("Use this template" button, or
`gh repo create <name> --template systems-researcher/systems-eng-paper-site`).
Set the owner to `systems-researcher` only if you are an org member and org
settings allow members to create repositories. Otherwise create the repo under
your own user and ask a maintainer to transfer it, or ask a maintainer to run
`gh repo create` for you.

## 2. Edit the one file

Everything you write lives in `content/paper.yaml`. That is the only file to
edit. Figure images go in `content/figures/`. An optional paper PDF goes at
`docs/paper.pdf`. Do not hand-edit anything else under `docs/`; the next
render overwrites it.

## 3. Required fields

`title`, `authors`, `year`, `licence`, `abstract`. The comments in
`content/paper.yaml` explain each one; empty values fail the build on purpose
so nothing half-filled gets published. Everything else in the file is
optional.

## 4. Turn Pages on

Settings, Pages, Deploy from a branch, branch `main`, folder `/docs`. This
setting is not copied from the template, so do it on every new repo before
announcing the URL. Once the repo is in the org, the URL is
`https://systems-researcher.github.io/<repo>/`.

## 5. Register on the index

Open a one-line PR adding an entry to `papers.yml` on
`systems-researcher/systems-eng-paper-site`. Required keys: `title`,
`authors`, `year`, `url`. Optional: `venue`.

## 6. Require the render check in branch protection

The template cannot force this. In your repo: Settings, Branches, branch
protection rules for `main`, require the `render` check to pass before
merging.

## 7. Update the renderer later

Templates copy files once. To take a renderer fix, copy `render/`,
`.github/workflows/render.yml`, `requirements.txt`, and `docs/assets/`
into your repo, except `docs/assets/figures/` (your figures) and a
paper-specific `docs/assets/og.png` (your social card). Commit and let the
Action re-render. Do not overwrite `content/paper.yaml`.

## Department index

The index footer links to the research programme:
https://systems-researcher.github.io/research-programme/
