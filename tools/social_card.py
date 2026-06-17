#!/usr/bin/env python3
"""Render the site-wide Open Graph card.

Rasterizes ``docs/assets/social-card-bg.svg`` to ``site/assets/social-card.png``
(1200x630) with cairosvg, using the vendored brand faces in ``tools/fonts/``.
Every page references the PNG through ``overrides/main.html``.

Run it AFTER ``zensical build`` (which writes and, with ``--clean``, wipes
``site/``); the card lands in the already-built tree just before deploy:

    uv run zensical-updates build
    uv run zensical build --clean --strict
    uv run python tools/social_card.py

Fonts are resolved through a throwaway fontconfig configuration that points only
at ``tools/fonts/``. That keeps rendering deterministic (no dependence on
system-installed fonts) and the CI build egress-free (no font download). cairosvg
renders through cairo's toy font API, which only distinguishes normal from bold,
so the SVG selects each weight by its full family name (for example
``Archivo ExtraBold``) rather than a numeric ``font-weight``.
"""

from __future__ import annotations

import argparse
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SVG = ROOT / "docs" / "assets" / "social-card-bg.svg"
DEFAULT_OUT = ROOT / "site" / "assets" / "social-card.png"
FONTS_DIR = ROOT / "tools" / "fonts"

WIDTH, HEIGHT = 1200, 630


def _configure_fontconfig(fonts_dir: Path) -> None:
    """Point fontconfig at ``fonts_dir`` only, via a temporary config.

    Sets ``FONTCONFIG_FILE`` before cairosvg (and the cairo/fontconfig it loads)
    is imported, so only the vendored faces are visible to the renderer.
    """
    tmp = Path(tempfile.mkdtemp(prefix="epf-social-card-"))
    cache_dir = tmp / "cache"
    cache_dir.mkdir()
    config = tmp / "fonts.conf"
    config.write_text(
        '<?xml version="1.0"?>\n'
        '<!DOCTYPE fontconfig SYSTEM "fonts.dtd">\n'
        "<fontconfig>\n"
        f"  <dir>{fonts_dir}</dir>\n"
        f"  <cachedir>{cache_dir}</cachedir>\n"
        "</fontconfig>\n"
    )
    os.environ["FONTCONFIG_FILE"] = str(config)


def render(svg_path: Path, out_path: Path, fonts_dir: Path = FONTS_DIR) -> Path:
    """Rasterize ``svg_path`` to ``out_path`` at 1200x630 and verify the result."""
    _configure_fontconfig(fonts_dir)
    # Imported after FONTCONFIG_FILE is set so cairo picks up the config.
    import cairosvg

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2png(
        url=str(svg_path),
        write_to=str(out_path),
        output_width=WIDTH,
        output_height=HEIGHT,
    )

    # Verify dimensions straight from the PNG IHDR (no extra dependency): an
    # 8-byte signature, then the IHDR chunk carrying big-endian width/height.
    data = out_path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise SystemExit("social card is not a valid PNG")
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if (width, height) != (WIDTH, HEIGHT):
        raise SystemExit(f"social card is {width}x{height}, expected {WIDTH}x{HEIGHT}")
    if len(data) < 5_000:
        raise SystemExit(f"social card is only {len(data)} bytes; render looks empty")
    print(f"social card: {out_path} ({width}x{height}, {len(data)} bytes)")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--svg", type=Path, default=DEFAULT_SVG, help="source SVG")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output PNG")
    args = parser.parse_args()
    render(args.svg, args.out)


if __name__ == "__main__":
    main()
