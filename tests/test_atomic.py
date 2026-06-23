import os

import pytest

import _atomic


def test_write_text_creates_file(tmp_path):
    dest = tmp_path / "out.txt"
    _atomic.write_text(dest, "hello")
    assert dest.read_text(encoding="utf-8") == "hello"


def test_write_bytes_creates_file(tmp_path):
    dest = tmp_path / "out.bin"
    _atomic.write_bytes(dest, b"\x00\x01\x02")
    assert dest.read_bytes() == b"\x00\x01\x02"


def test_write_creates_parent_dirs(tmp_path):
    dest = tmp_path / "a" / "b" / "out.txt"
    _atomic.write_text(dest, "deep")
    assert dest.read_text(encoding="utf-8") == "deep"


def test_write_replaces_existing(tmp_path):
    dest = tmp_path / "out.txt"
    dest.write_text("old", encoding="utf-8")
    _atomic.write_text(dest, "new")
    assert dest.read_text(encoding="utf-8") == "new"


def test_write_leaves_no_temp_file(tmp_path):
    dest = tmp_path / "out.txt"
    _atomic.write_text(dest, "hello")
    # The only file in the directory is the destination; no .tmp straggler.
    assert [p.name for p in tmp_path.iterdir()] == ["out.txt"]


def test_write_new_file_follows_umask(tmp_path):
    dest = tmp_path / "out.txt"
    _atomic.write_text(dest, "hello")
    mask = os.umask(0)
    os.umask(mask)
    assert (dest.stat().st_mode & 0o777) == (0o666 & ~mask)


def test_write_preserves_existing_mode(tmp_path):
    dest = tmp_path / "out.txt"
    dest.write_text("old", encoding="utf-8")
    os.chmod(dest, 0o600)
    _atomic.write_text(dest, "new")
    # An overwrite keeps the destination's prior permissions, like a normal write.
    assert (dest.stat().st_mode & 0o777) == 0o600


def test_encode_error_writes_nothing(tmp_path):
    dest = tmp_path / "out.txt"
    # A surrogate fails to encode before any temp file is opened, so nothing
    # is created at all.
    with pytest.raises(UnicodeEncodeError):
        _atomic.write_text(dest, "\ud800")
    assert list(tmp_path.iterdir()) == []
    assert not dest.exists()


def test_replace_failure_cleans_up_temp(tmp_path, monkeypatch):
    dest = tmp_path / "out.txt"

    def boom(*args, **kwargs):
        raise OSError("replace failed")

    # The temp file is created and written, then the rename fails: the cleanup
    # branch must remove the temp and re-raise, leaving the directory clean.
    monkeypatch.setattr(_atomic.os, "replace", boom)
    with pytest.raises(OSError, match="replace failed"):
        _atomic.write_text(dest, "hello")
    assert list(tmp_path.iterdir()) == []
    assert not dest.exists()


def test_replace_failure_preserves_existing_destination(tmp_path, monkeypatch):
    dest = tmp_path / "out.txt"
    dest.write_text("old", encoding="utf-8")

    def boom(*args, **kwargs):
        raise OSError("replace failed")

    # A failed write never corrupts the prior file: the destination keeps its
    # old content and no temp straggler is left behind.
    monkeypatch.setattr(_atomic.os, "replace", boom)
    with pytest.raises(OSError, match="replace failed"):
        _atomic.write_text(dest, "new")
    assert dest.read_text(encoding="utf-8") == "old"
    assert [p.name for p in tmp_path.iterdir()] == ["out.txt"]
