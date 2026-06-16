# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). This site deploys
continuously, so entries accumulate under [Unreleased].

## [Unreleased]

### Added

- uv build environment: `pyproject.toml` and `uv.lock` pinning zensical
  (`>=0.0.45,<0.1`) and the `zensical-blog` plugin (git commit pin).
- Minimal `zensical.toml` and a placeholder home page. The scaffold builds with
  `uv run zensical build --clean --strict`.
