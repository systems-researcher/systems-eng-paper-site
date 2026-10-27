# Style pick

Chosen: A on 2026-10-27.
Accent hex: #0F5257. Masthead rule: 3px double. Emblem: circle monogram SE. Annotation underline: kept.

Contrast, body text (`--fg` on named background), computed chosen tokens:

| Scheme | Pair | Ratio |
|---|---|---|
| light | `--fg` on `--bg` | 15.62:1 |
| light | `--fg` on `--bg-deep` | 14.37:1 |
| dark | `--fg` on `--bg` | 14.21:1 |
| dark | `--fg` on `--bg-deep` | 12.88:1 |

All four pairs clear 4.5:1 body floor. Display accent on background: light 7.98:1, dark 8.42:1 (both above 3:1). Relative luminance, sRGB. No `--fg`/`--bg` retune needed.

Dark scheme accent uses `--se-petrol-on-dark` (#7DC0C0) so the petrol family holds in both schemes. `ACCENT_KEYS` stays `petrol` only.

## Visual check

taste-skill read: editorial academic paper site for public-sector / department trust; dials variance 4, motion 2, density 4.

Findings fixed inside allowed set:

- `.byline` and `.links` had no rules; added flex row, muted byline, weight on link row.
- `.emblem` sized to 2.5rem with small trailing gap; color from `--accent`.
- `.logo-slot` kept hidden, reserved 2.5rem box and `margin-left: auto` for when the official LU mark lands.

Not changed (outside difference set): `.sheet` layout, dark pair structure, EB Garamond + IBM Plex Sans, no CDN.

Screenshot pass (Playwright, light + dark, `prefers-color-scheme`). visual-judge skipped (HTML site, not pptx/docx/pdf). Paths under `docs/_style-check/shots/` (gitignored build artifact):

| Page | Light | Dark |
|---|---|---|
| Paper with figures | paper-figures-light.png | paper-figures-dark.png |
| Paper without figures | paper-no-figures-light.png | paper-no-figures-dark.png |
| Index two entries (static `.ledger` stand-in) | index-two-light.png | index-two-dark.png |
| Index empty | index-empty-light.png | index-empty-dark.png |
| Paper at max-width 40rem | paper-narrow-light.png | paper-narrow-dark.png |

Canonical freeze:

- `docs/assets/tokens.css` (from candidate A)
- `docs/assets/emblem.svg`
- `render/assets/emblem.svg`

Suffixed `tokens-*` / `emblem-*` and `style-candidates/` removed after freeze.
