# Style pick

Chosen: Loughborough Floot re-style 2026-10-28.
Accent hex (petrol key value): #CD0067 magenta. Masthead: solid #330065 band (CSS-only). Emblem: circle monogram SE, currentColor white on purple. Annotation underline: kept. Display: Instrument Serif 400 + italic. Body: IBM Plex Sans. Meta/fig numerals: IBM Plex Mono 400. Self-hosted OFL only; no CDN.

Contrast, body text (`--fg` on named background), computed chosen tokens (relative luminance, sRGB):

| Scheme | Pair | Ratio |
|---|---|---|
| light | `--fg` (#1F1433) on `--bg` (#F7F4FA) | 15.98:1 |
| light | `--fg` (#1F1433) on `--bg-deep` (#D9CCE8) | 11.40:1 |
| dark | `--fg` (#F7F4FA) on `--bg` (#1F1433) | 15.98:1 |
| dark | `--fg` (#F7F4FA) on `--bg-deep` (#3D3550) | 10.57:1 |

All four pairs clear 4.5:1 body floor. Extra pairs: white on #330065 15.81:1; #330065 body links on plate 14.51:1; magenta #CD0067 on plate 5.08:1 (large/heading/accent only); dark accent #F2A6CC on #1F1433 9.20:1 (above 3:1 UI). Magenta not used for small body links.

Dark scheme accent uses `--se-petrol-on-dark` (#F2A6CC). `ACCENT_KEYS` stays `petrol` only; token value remapped.

## Fonts

| Role | Family | Files |
|---|---|---|
| Display | Instrument Serif 400 / 400 italic | `instrument-serif-latin-400-normal.woff2`, `instrument-serif-latin-400-italic.woff2`, `InstrumentSerif-OFL.txt` |
| Body | IBM Plex Sans 400 / 400 italic / 600 | existing `ibm-plex-sans-latin-*.woff2`, `OFL-IBM-Plex-Sans.txt` (covers Mono) |
| Mono | IBM Plex Mono 400 | `ibm-plex-mono-latin-400-normal.woff2` |

EB Garamond dropped (no remaining CSS refs).

## Visual check

taste-skill read: editorial academic paper site, Loughborough department palette; dials variance 4, motion 2, density 4.

Findings fixed inside allowed set (CSS only):

- Masthead deep-purple band via `.masthead` background; brand + emblem inherit white.
- Body links use `--link` (#330065 light / pink dark); magenta reserved for large accent (`.fig-n`, `.ledger-id`, hover).
- `.sec-n` Instrument Serif near-black (`--fg`); focus-visible outline on link purple.
- `.record` dl and `.byline` / `.fig-n` / `.cite` use mono strip.
- reduced-motion keeps annot underline fully drawn; forced-colors masthead fallback.

Screenshot pass (Playwright, light + dark, `prefers-color-scheme`). Paths under `docs/_style-check/shots/` (gitignored build artifact).

Canonical freeze:

- `docs/assets/tokens.css`
- `docs/assets/site.css`
- `docs/assets/emblem.svg`
- `render/assets/emblem.svg`
- `docs/assets/fonts/` (Instrument Serif + Plex Sans + Plex Mono)
