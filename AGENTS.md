# AGENTS.md

Guidance for AI coding/review agents (Codex, etc.) working in this repo.
Humans: see `README.md`. Claude Code: see `CLAUDE.md` (more detailed).

## What this is

The public site for Ivan Anishchuk's Ethereum Protocol Fellowship (EPF)
cohort-seven dev updates: a documentation-style hub plus an "Updates" blog,
built with zensical and deployed to GitHub Pages. The content outlives the
fellowship as a public record. See `PLAN.md` for the staged build plan.

## Setup & checks

```bash
uv sync                              # install the pinned build environment
uv run zensical-updates build        # generate the Updates section (docs/updates/)
uv run zensical build --clean --strict   # the strict build gate
uv run python tools/social_card.py   # rasterize the social card into site/
uv run zensical serve                # local preview at http://localhost:8000
```

The three build steps are the gate, in that order: `zensical-updates build`
generates `docs/updates/` (the nav points at `docs/updates/index.md`, which only
exists after this step), then `zensical build --clean --strict` builds the site,
then `tools/social_card.py` writes the card into the built tree (it runs after
the build because `--clean` wipes `site/`).

## Conventions

- Build environment is Python 3.14 (`requires-python = "==3.14.*"`), uv-native;
  pins live in `pyproject.toml` and `uv.lock`. Site config is `zensical.toml`.
- Generated trees are gitignored and never committed: `site/` and `docs/updates/`.
  Commit only the `updates/` sources, `pyproject.toml`/`uv.lock`, and config.
- Dev-update posts live at `updates/YYYY-MM-DD-<slug>.md` outside `docs/`. The
  dated filename stem is the URL segment; keep the `date:` front matter in sync.
  Give every post an explicit `title:`. Write `categories`/`tags` as YAML block
  lists (`- weekly-update`), never flow lists: zensical's strict link check reads
  `[x]` in front matter as a Markdown reference link and fails the build. Allowed
  categories: weekly-update, project-update, news.
- The Updates blog and social cards are our own additions on top of zensical
  (the generator is the separate `zensical-updates` sidecar). zensical does not
  yet ship either.
- GitHub Actions are pinned to full commit SHAs; workflow permissions are
  least-privilege with `persist-credentials: false` and a harden-runner step.

## Hard rules

- **Dev-update prose is the fellow's own writing (no-LLM).** EPF requires it.
  An agent may scaffold a post (front matter, headings, a links checklist) and
  may copy-edit a finished draft. An agent must never write the body prose of a
  weekly dev update. The hub, about, and project pages may be agent-drafted, then
  Ivan rewrites them in his own voice.
- **No third-party artwork committed.** Ethereum Foundation visuals are style
  inspiration only. Per-page social cards come from our own build step (theme
  colors, our logo, the page title).
- **Public repo hygiene.** No secrets, no large media, no build output.

## Writing style

Binds on docs, comments, commit messages, and PR text.

- No em-dashes used as subphrase separators. Use commas, or split into two
  sentences.
- No contrastive negation. State the positive directly instead of "not X, but Y".
- Vary sentence length. Prefer active voice.
- No filler openers or summary closers.
- Avoid AI-tell vocabulary (delve, leverage, robust, seamless, tapestry,
  landscape, and similar).

## Review guidelines

Focus on correctness and the invariants above. Flag, in priority order:

- **Build correctness:** changes to `zensical.toml`, `pyproject.toml`,
  `tools/social_card.py`, or the workflow that would break the strict build or
  the card render. Imports go at the top of any Python file.
- **CI hardening (deliberate, do NOT "fix"):** SHA-pinned actions, top-level
  `permissions: {}` with per-job least-privilege grants, `persist-credentials:
  false`, harden-runner.
- **Front matter:** flow-list `categories`/`tags`, a missing `title:`, or a
  missing page `description:`.
- **The no-LLM rule:** never propose rewrites of weekly dev-update body prose.

Prefer a few high-confidence, high-severity findings over many low-value ones.
A green or empty automated review is not a human approval.
