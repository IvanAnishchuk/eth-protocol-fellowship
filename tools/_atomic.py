"""Atomic file writes for the build tools.

Write to a temp file in the destination directory, then ``os.replace`` it into
place. ``os.replace`` is atomic on the same filesystem, so a reader, or a build
killed mid-write, never sees a half-written file: the destination holds either
the old content or the complete new content, never a truncated mix. The temp
file shares the destination's directory so the rename stays on one filesystem,
and it lands with the mode a normal write would leave: an existing file keeps
its own permissions, a new one follows the active umask.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


def _target_mode(path: Path) -> int:
    """The permission bits a normal write would leave for ``path``."""
    try:
        return os.stat(path).st_mode & 0o777  # an overwrite keeps the file's mode
    except FileNotFoundError:
        mask = os.umask(0)
        os.umask(mask)
        return 0o666 & ~mask  # a new file follows the umask


def _write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = _target_mode(path)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    os.close(fd)  # keep the reserved name; write through the path so no fd leaks
    try:
        with open(tmp, "wb") as handle:
            handle.write(data)
        os.chmod(tmp, mode)
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
