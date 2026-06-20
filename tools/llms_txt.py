#!/usr/bin/env python3
"""Generate site/llms.txt from a curated header plus the post list.

Hybrid model: tools/llms.head.md carries the hand-written header (summary and
hub pages) ending in a ``<!-- updates -->`` marker; this step renders an Updates
section from the updates/*.md front matter and splices it in. Run after
``zensical build`` (it writes into the built site/):

    uv run python tools/llms_txt.py

Every post in updates/ shows up, sorted newest first, so the list cannot drift
from the actual posts.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
HEADER = ROOT / "tools" / "llms.head.md"
UPDATES_DIR = ROOT / "updates"
CONFIG = ROOT / "zensical.toml"
OUT = ROOT / "site" / "llms.txt"
MARKER = "<!-- updates -->"


def parse_front_matter(text: str) -> dict:
    """Parse a leading ``---``-delimited YAML front-matter block; {} if absent."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    data = yaml.safe_load(text[3:end])
    return data if isinstance(data, dict) else {}


def post_url(stem: str, site_url: str) -> str:
    """Map a post file stem to its built URL (site_url ends with '/')."""
    return f"{site_url}updates/{stem}/"


def load_posts(updates_dir: Path) -> list[dict]:
    """Read updates/*.md (excluding index.md) into post dicts."""
    posts = []
    for path in updates_dir.glob("*.md"):
        if path.stem == "index":
            continue
        meta = parse_front_matter(path.read_text(encoding="utf-8"))
        posts.append(
            {
                "stem": path.stem,
                "title": meta.get("title", path.stem),
                "date": str(meta.get("date", "")),
                "description": meta.get("description", ""),
            }
        )
    return posts


def render_updates(posts: list[dict], site_url: str) -> str:
    """Render the ``## Updates`` section, newest first."""
    lines = ["## Updates", ""]
    for post in sorted(posts, key=lambda p: p["date"], reverse=True):
        url = post_url(post["stem"], site_url)
        suffix = f": {post['description']}" if post["description"] else ""
        lines.append(f"- [{post['title']}]({url}){suffix}")
    return "\n".join(lines)


def splice(header: str, section: str, marker: str = MARKER) -> str:
    """Replace the marker in header with section (error if the marker is gone)."""
    if marker not in header:
        raise ValueError(f"marker {marker!r} not found in header")
    return header.replace(marker, section)


def site_url_from_config(config_path: Path) -> str:
    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    return data["project"]["site_url"]


def build() -> str:
    header = HEADER.read_text(encoding="utf-8")
    site_url = site_url_from_config(CONFIG)
    section = render_updates(load_posts(UPDATES_DIR), site_url)
    return splice(header, section)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    content = build()
    OUT.write_text(content, encoding="utf-8")
    print(f"llms.txt: {OUT} ({len(content)} bytes)")


if __name__ == "__main__":
    main()
