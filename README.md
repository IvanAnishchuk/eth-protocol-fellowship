# eth-protocol-fellowship

The public site for Ivan Anishchuk's Ethereum Protocol Fellowship (EPF)
cohort-seven dev updates and project updates. A hub page plus an "Updates" blog,
built with zensical and deployed to GitHub Pages at
<https://ivananishchuk.github.io/eth-protocol-fellowship/>.

## Status

Skeleton. The build follows the staged plan in `PLAN.md`. This repo currently
holds the conventions (`CLAUDE.md`), the build plan (`PLAN.md`), the license, and
starter artwork in `docs/assets/`.

## Local preview

Once the build is scaffolded (Phase 0 of `PLAN.md`):

```sh
uv run zensical serve                      # preview at http://localhost:8000
uv run zensical build --clean --strict     # the build gate
```

## Layout

- `docs/` — site content (the hub pages and the `blog/` updates).
- `docs/assets/` — logo, favicon, and the social-card template.
- `zensical.toml` — site configuration (added in Phase 1).
- `CLAUDE.md` — conventions and hard rules for anyone working here.
- `PLAN.md` — the staged build plan.

## License

Released to the public domain under CC0-1.0. See `LICENSE.md`.
