# Modernization plan

Working notes for turning this repo into an automated, multi-language,
web-published manual. Being built out incrementally on
`robthomson/ethos-manual` before anything goes near `FrSkyRC/ethos-manual`.

## Current state (as of this phase)

Two pipelines coexist:

- **English / Italian / German / Spanish**: authored by hand in
  LibreOffice **ODT**, exported to PDF, both committed as binaries per
  revision. No web output. Spanish lags noticeably behind English.
- **French** (`french/`, plus an unfinished `french_LT/`): **Markdown**,
  GitBook `SUMMARY.md` table of contents, hosted externally on
  gitbook.io, PDF auto-built via `.github/workflows/french-pdf.yml`
  (pandoc + xetex).
- **Japanese**: not started.

Screenshot generation (`manual/`, `websim/`, `forge/` per language —
simulator + Lua macros driving `.bin` model files) is already automated
and is being kept as-is; it's the one part of the current pipeline that
doesn't need rework.

`.git` history is ~3.2GB (binaries committed uncompressed, no LFS). Per
decision below, not being rewritten right now — just stopping it from
getting worse.

## Decisions made

| Question | Decision |
|---|---|
| English source format | Convert ODT → Markdown, becomes the canonical source (Phase 2) |
| Site generator | MkDocs + Material |
| Repo history (3.2GB `.git`, no LFS) | Fix going forward only — LFS tracks new binaries via `.gitattributes`; existing history untouched |

## Phases

- **Phase 0 — Foundations** ✅ this change
  - `.gitattributes`: LFS tracking for new `*.png *.jpg *.jpeg *.odt *.pdf
    *.bin *.frsk *.ods`. Run `git lfs install` locally once before adding
    any new files of these types.
  - `mkdocs.yml`, `requirements-docs.txt`, `tools/summary_to_nav.py`.
- **Phase 1 — Prove the pipeline on French** ✅ this change
  - `mkdocs.yml` builds `french/` only, Material theme, nav generated
    from `french/SUMMARY.md` by `tools/summary_to_nav.py`.
  - `.github/workflows/pages.yml` builds and deploys to GitHub Pages on
    push to `french/**` (branch `manual-online`), or manually.
  - Fixed: `french/.gitbook/assets/` (dot-directory, invisible to any
    non-GitBook renderer including this one) renamed to
    `french/gitbook-legacy-assets/assets/`, with the ~135 references
    across 9 files repointed. This was already effectively broken for
    anyone not viewing on gitbook.io.
- **Phase 2 — English ODT → Markdown** (not started)
  - Pandoc first pass, Claude-assisted structural cleanup per chapter,
    human review chapter-by-chapter. Restructure into per-chapter files
    mirroring French's layout so chapter structure is consistent across
    languages — that consistency is what makes automated translation
    mapping tractable in Phase 3.
- **Phase 3 — Claude translation Action** (not started)
  - On English markdown changes, diff changed sections; call the Claude
    API per target language with the diff + existing translation +
    a glossary sourced from Ethos's own translated firmware UI strings
    (not invented terms); open one PR per language for human review.
    Never auto-merge — this is safety-relevant configuration guidance.
  - Track last-translated EN commit per chapter in
    `translations/state.json` so re-runs stay incremental.
- **Phase 4 — Bootstrap German / Italian / Spanish / Japanese** (not started)
  - Same pipeline, one-time full translation from the new EN markdown
    master, each behind a human-review PR, replacing the ODT process.
- **Phase 5 — Cutover** (not started)
  - All languages on GitHub Pages with a language switcher
    (mkdocs-static-i18n). Retire gitbook.io hosting and fold
    `french-pdf.yml` into the unified build+deploy+PDF workflow.

## Known content gaps surfaced by the Phase 1 build (not fixed here)

Pre-existing in the GitBook content, not introduced by this migration —
flagging rather than silently patching:

- `configuration-du-modele/edition-modele.md`: broken links to
  `assets/model-icon-edit.png` and `assets/model-edit.png` (files don't
  exist in `assets/`).
- `configuration-du-systeme/materiel.md`: broken link to
  `assets/system-hardware-check.png`.
- `configuration-du-systeme/information.md`: broken link to
  `assets/system-info-internal-module.png`.
- `configurer-les-ecrans/*.md`: several `![](../.gitbook/assets/????????.jpeg)`
  links where the filename itself was mangled (no matching file exists
  under any name) — unrecoverable without the original image.
- Pages that exist on disk but aren't listed in `french/SUMMARY.md` (so
  also missing from `mkdocs.yml`'s `nav`): `styles.md`, and the two
  tutorial section `README.md` index pages under
  `Tutoriels-de-programmation/Exemple-d-avion-a-voilure-fixe-de-base/`
  and `.../Exemple-de-configuration-radio-initiale/`.

Once these are cleaned up, switch `mkdocs build` to `mkdocs build
--strict` in `.github/workflows/pages.yml` so future breakages fail CI
instead of just logging a warning.

## One manual step required (can't be done from the CLI)

In the fork's GitHub repo settings: **Settings → Pages → Source: GitHub
Actions**. Everything else is driven by the workflow.
