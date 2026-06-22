import pytest

import llms_txt


def test_parse_front_matter_reads_scalars():
    text = (
        "---\n"
        'title: "EPF Week 0"\n'
        "date: 2026-06-17\n"
        'description: "A week: scoping things."\n'
        "---\n"
        "# Body\n"
    )
    meta = llms_txt.parse_front_matter(text)
    assert meta["title"] == "EPF Week 0"
    assert str(meta["date"]) == "2026-06-17"
    assert meta["description"] == "A week: scoping things."


def test_parse_front_matter_absent_returns_empty():
    assert llms_txt.parse_front_matter("# No front matter\n") == {}


def test_post_url_builds_dated_segment():
    url = llms_txt.post_url("2026-06-17-week-0", "https://example.com/epf/")
    assert url == "https://example.com/epf/updates/2026-06-17-week-0/"


def test_post_url_adds_missing_slash():
    url = llms_txt.post_url("2026-01-01-x", "https://example.com/epf")
    assert url == "https://example.com/epf/updates/2026-01-01-x/"


def test_load_posts_reports_bad_front_matter(tmp_path):
    (tmp_path / "2026-01-01-bad.md").write_text(
        "---\ntitle: [unclosed\n---\n# body\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="invalid front matter"):
        llms_txt.load_posts(tmp_path)


def test_render_updates_orders_newest_first():
    posts = [
        {"stem": "2026-06-03-a", "title": "A", "date": "2026-06-03", "description": "older"},
        {"stem": "2026-06-17-b", "title": "B", "date": "2026-06-17", "description": "newer"},
    ]
    out = llms_txt.render_updates(posts, "https://example.com/epf/")
    assert out.splitlines()[0] == "## Updates"
    assert out.index("/updates/2026-06-17-b/") < out.index("/updates/2026-06-03-a/")
    assert "- [B](https://example.com/epf/updates/2026-06-17-b/): newer" in out


def test_render_updates_sorts_by_date_value_not_string():
    # A garbage/empty date must not outrank a real date the way a raw string
    # sort does ("not-a-date" > "2026-..." lexically); parsed dates win.
    posts = [
        {"stem": "baddate", "title": "B", "date": "not-a-date", "description": ""},
        {"stem": "nodate", "title": "N", "date": "", "description": ""},
        {"stem": "dated", "title": "D", "date": "2026-06-17", "description": ""},
    ]
    out = llms_txt.render_updates(posts, "https://example.com/epf/")
    items = [line for line in out.splitlines() if line.startswith("- ")]
    assert "/updates/dated/" in items[0]


def test_render_updates_escapes_brackets_in_title():
    posts = [{"stem": "s", "title": "Week [draft]", "date": "2026-01-01", "description": ""}]
    out = llms_txt.render_updates(posts, "https://example.com/epf/")
    assert r"[Week \[draft\]]" in out


def test_render_updates_omits_empty_description():
    posts = [{"stem": "s", "title": "T", "date": "2026-01-01", "description": ""}]
    out = llms_txt.render_updates(posts, "https://example.com/epf/")
    assert "- [T](https://example.com/epf/updates/s/)" in out
    assert "): " not in out


def test_splice_replaces_marker():
    header = "# Title\n\n## Pages\n\n<!-- updates -->\n"
    out = llms_txt.splice(header, "## Updates\n\n- [x](y)")
    assert "<!-- updates -->" not in out
    assert "## Updates" in out


def test_splice_missing_marker_raises():
    with pytest.raises(ValueError):
        llms_txt.splice("no marker here", "## Updates")
