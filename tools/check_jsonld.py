#!/usr/bin/env python3
"""Validate the JSON-LD structured data in the built site.

Walks the built site/ tree, parses every ``<script type="application/ld+json">``
block (failing on any that is not valid JSON), and asserts that the key page
types carry the expected schema.org @types. Run after ``zensical build``:

    uv run python tools/check_jsonld.py

Exits non-zero on the first problem so it works as a CI gate.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
UPDATES_SRC = ROOT / "updates"

# Tolerant of attribute order, quoting, and extra attributes (e.g. a CSP
# nonce): a markup tweak should not silently match zero blocks and mis-report.
SCRIPT_RE = re.compile(
    r'<script\b[^>]*\stype\s*=\s*(?P<q>["\'])application/ld\+json(?P=q)[^>]*>'
    r"(?P<body>.*?)</script>",
    re.DOTALL | re.IGNORECASE,
)


def _add_types(node: object, types: set[str]) -> None:
    """Add a node's @type(s) to the set; @type may be a string or a list."""
    if not isinstance(node, dict):
        return
    node_type = node.get("@type")
    if isinstance(node_type, str):
        types.add(node_type)
    elif isinstance(node_type, list):
        types.update(t for t in node_type if isinstance(t, str))


def extract_graph_types(html: str) -> set[str]:
    """Set of @type values across the JSON-LD nodes (raises on bad JSON).

    Handles both the ``@graph`` form and a single top-level node, and a
    ``@type`` that is a string or a list.
    """
    types: set[str] = set()
    for match in SCRIPT_RE.finditer(html):
        data = json.loads(match.group("body"))
        if isinstance(data, dict):
            graph = data.get("@graph")
            if isinstance(graph, list):
                for node in graph:
                    _add_types(node, types)
            else:
                _add_types(data, types)
        elif isinstance(data, list):
            for node in data:
                _add_types(node, types)
    return types


def check() -> list[str]:
    """Return a list of problem strings; empty means all good."""
    problems: list[str] = []

    def require(rel: str, expected: set[str]) -> None:
        path = SITE / rel
        if not path.exists():
            problems.append(f"missing built page: {rel}")
            return
        try:
            found = extract_graph_types(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            problems.append(f"invalid JSON-LD in {rel}: {exc}")
            return
        missing = expected - found
        if missing:
            problems.append(
                f"{rel}: missing @type(s) {sorted(missing)} (found {sorted(found)})"
            )

    require("index.html", {"WebSite", "Person"})
    require("about/index.html", {"ProfilePage", "Person", "BreadcrumbList"})
    require("project/index.html", {"WebPage", "BreadcrumbList"})
    require("updates/index.html", {"Blog", "BreadcrumbList"})

    posts = sorted(p.stem for p in UPDATES_SRC.glob("*.md") if p.stem != "index")
    if not posts:
        problems.append("no source posts found in updates/*.md")
    for stem in posts:
        require(f"updates/{stem}/index.html", {"BlogPosting", "BreadcrumbList"})

    return problems


def main() -> None:
    problems = check()
    if problems:
        print("JSON-LD validation failed:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        raise SystemExit(1)
    print("JSON-LD: all checked pages carry the expected structured data")


if __name__ == "__main__":
    main()
