#!/usr/bin/env python3
"""Read and validate the zensical config fields the build and templates depend on.

``site_url`` is the load-bearing one. overrides/main.html (a MiniJinja template
with no string methods) and the build tools form absolute URLs by concatenating
onto it (``config.site_url ~ "updates/"``), and the homepage JSON-LD branch
matches ``page.canonical_url == config.site_url``. The template cannot normalize
itself, so the build gate validates the invariant here instead. Both
tools/check_jsonld.py and tools/llms_txt.py read ``site_url`` through this module.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "zensical.toml"


def site_url_from_config(config_path: Path = CONFIG) -> str:
    """Read ``project.site_url`` from the zensical config (raises if absent)."""
    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    return data["project"]["site_url"]


def check_site_url(site_url: object) -> list[str]:
    """Problems with a ``site_url`` value; empty means it holds every invariant.

    The site relies on ``site_url`` being an absolute URL that ends in ``/``:
    the template builds the og:image, the RSS href, and the JSON-LD
    breadcrumb/``@id`` URLs by concatenating onto it, and the homepage branch
    matches ``page.canonical_url == config.site_url``. A relative or slash-less
    value corrupts all of those at once, and the build only asserts @type
    presence, so the malformed URLs would otherwise pass the gate green.
    """
    if not isinstance(site_url, str):
        return [f"site_url must be a string: {site_url!r}"]
    problems: list[str] = []
    if not site_url.startswith(("http://", "https://")):
        problems.append(
            f"site_url must be an absolute URL (scheme and host): {site_url!r}"
        )
    if not site_url.endswith("/"):
        problems.append(
            f"site_url must end with '/' (templates concatenate paths onto it): "
            f"{site_url!r}"
        )
    return problems


def site_url_problems(config_path: Path = CONFIG) -> list[str]:
    """Read and validate ``project.site_url``, returning gate-message problems.

    Reads gracefully so a missing or unreadable config becomes a reported
    problem rather than an uncaught traceback: check() then surfaces it next to
    the JSON-LD problems instead of crashing the gate.
    """
    try:
        site_url = site_url_from_config(config_path)
    except OSError as exc:
        return [f"cannot read config {config_path}: {exc}"]
    except tomllib.TOMLDecodeError as exc:
        return [f"invalid TOML in {config_path}: {exc}"]
    except (KeyError, TypeError):
        return [f"config {config_path} has no project.site_url"]
    return check_site_url(site_url)
