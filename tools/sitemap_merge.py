#!/usr/bin/env python3
"""Compile every sitemap the build produced into one root sitemap.

zensical writes site/sitemap.xml covering its ``nav`` pages only; the
zensical-updates sidecar writes a sitemap for the generated Updates section at
site/updates/sitemap.xml (the posts and taxonomy pages, which are not in nav).
A crawler reads a single sitemap at the site root, so this step unions every
``<loc>`` across the sitemaps under site/ into one de-duplicated
site/sitemap.xml, leaving each section sitemap in place. Run after
``zensical build`` and the sidecar build, so every input sitemap exists:

    uv run python tools/sitemap_merge.py

The ``<loc>``s are already absolute, so this only copies and de-dups them, with
no knowledge of which URLs belong to which producer. Merging the merged root
with its sources is a fixpoint, so a re-run reproduces the same file; no
wall-clock value is written, so rebuilding the same content is byte-identical.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from _atomic import write_text

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
ROOT_SITEMAP = "sitemap.xml"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
_URL = f"{{{NS}}}url"
_LOC = f"{{{NS}}}loc"


def extract_locs(xml_text: str) -> list[str]:
    """The ``<loc>`` of each ``<url>`` in a sitemap, in document order.

    Reads only ``<url>`` entries, so a ``<sitemapindex>``'s ``<sitemap><loc>``
    references (which point at other sitemaps, not pages) are ignored.
    """
    root = ET.fromstring(xml_text)
    locs = []
    for url in root.iter(_URL):
        loc = url.findtext(_LOC)
        if loc and loc.strip():
            locs.append(loc.strip())
    return locs


def discover_sitemaps(site_dir: Path) -> list[Path]:
    """Every ``sitemap.xml`` under site_dir: the root one first, then nested, sorted."""
    root_sitemap = site_dir / ROOT_SITEMAP
    nested = sorted(p for p in site_dir.rglob(ROOT_SITEMAP) if p != root_sitemap)
    return [root_sitemap, *nested]


def merge_locs(sitemaps: list[Path]) -> list[str]:
    """Union the ``<loc>``s across sitemaps, de-duplicated, first occurrence wins."""
    seen: dict[str, None] = {}
    for path in sitemaps:
        for loc in extract_locs(path.read_text(encoding="utf-8")):
            seen.setdefault(loc, None)
    return list(seen)


def render_sitemap(locs: list[str]) -> str:
    """Build urlset XML with one ``<url><loc>`` per location, in order."""
    ET.register_namespace("", NS)
    urlset = ET.Element(f"{{{NS}}}urlset")
    for loc in locs:
        url = ET.SubElement(urlset, _URL)
        ET.SubElement(url, _LOC).text = loc
    ET.indent(urlset, space="  ")
    body = ET.tostring(urlset, encoding="unicode")
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{body}\n'


def merge_sitemaps(site_dir: Path) -> list[str]:
    """Union all sitemaps under site_dir into site_dir/sitemap.xml; return the locs."""
    root_sitemap = site_dir / ROOT_SITEMAP
    if not root_sitemap.exists():
        raise FileNotFoundError(f"no sitemap to merge at {root_sitemap}")
    locs = merge_locs(discover_sitemaps(site_dir))
    write_text(root_sitemap, render_sitemap(locs))
    return locs


def main() -> None:
    locs = merge_sitemaps(SITE)
    print(f"sitemap: {SITE / ROOT_SITEMAP} ({len(locs)} URLs)")


if __name__ == "__main__":
    main()
