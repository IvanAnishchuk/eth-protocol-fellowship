"""Atomic file writes for the build tools.

Write to a temp file in the destination directory, then ``os.replace`` it into
place. ``os.replace`` is atomic on the same filesystem, so a reader, or a build
killed mid-write, never sees a half-written file: the destination holds either
the old content or the complete new content, never a truncated mix. The temp
file shares the destination's directory so the rename stays on one filesystem.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


def _write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.chmod(tmp, 0o644)  # mkstemp creates 0600; match a normal file write
        os.replace(tmp, path)
    except BaseException:
        # A failed write or replace must not leave the temp file behind.
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    """Atomically write text to path, creating parent directories as needed."""
    _write(path, text.encode(encoding))


def write_bytes(path: Path, data: bytes) -> None:
    """Atomically write bytes to path, creating parent directories as needed."""
    _write(path, data)
