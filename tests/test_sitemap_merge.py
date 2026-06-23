import xml.etree.ElementTree as ET

import pytest

import sitemap_merge

NS = sitemap_merge.NS


def _urlset(*locs):
    urls = "".join(f"<url><loc>{loc}</loc></url>" for loc in locs)
    return f'<urlset xmlns="{NS}">{urls}</urlset>'


def _write(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def test_extract_locs_reads_urls_in_order():
    xml = _urlset("https://x/a/", "https://x/b/")
    assert sitemap_merge.extract_locs(xml) == ["https://x/a/", "https://x/b/"]


def test_extract_locs_ignores_index_entries():
    # A <sitemapindex> points only at other sitemaps; those locs are skipped.
    index = f'<sitemapindex xmlns="{NS}"><sitemap><loc>https://x/s.xml</loc></sitemap></sitemapindex>'
    assert sitemap_merge.extract_locs(index) == []


def test_extract_locs_handles_encoding_declaration():
    # zensical's sitemap.xml carries an <?xml ... encoding=...?> declaration; a
    # str carrying it must still parse (stdlib ElementTree tolerates this).
    xml = f'<?xml version="1.0" encoding="UTF-8"?>{_urlset("https://x/a/")}'
    assert sitemap_merge.extract_locs(xml) == ["https://x/a/"]


def test_discover_sitemaps_root_first_then_nested_sorted(tmp_path):
    _write(tmp_path / "sitemap.xml", _urlset("https://x/"))
    _write(tmp_path / "updates" / "sitemap.xml", _urlset("https://x/updates/"))
    _write(tmp_path / "blog" / "sitemap.xml", _urlset("https://x/blog/"))
    found = sitemap_merge.discover_sitemaps(tmp_path)
    assert found == [
        tmp_path / "sitemap.xml",
        tmp_path / "blog" / "sitemap.xml",
        tmp_path / "updates" / "sitemap.xml",
    ]


def test_merge_locs_dedupes_first_occurrence_wins(tmp_path):
    _write(tmp_path / "sitemap.xml", _urlset("https://x/", "https://x/updates/"))
    _write(tmp_path / "updates" / "sitemap.xml", _urlset("https://x/updates/", "https://x/updates/p/"))
    locs = sitemap_merge.merge_locs(sitemap_merge.discover_sitemaps(tmp_path))
    assert locs == ["https://x/", "https://x/updates/", "https://x/updates/p/"]


def test_render_sitemap_emits_urlset_without_prefix():
    xml = sitemap_merge.render_sitemap(["https://x/a/", "https://x/b/"])
    root = ET.fromstring(xml)
    assert root.tag == f"{{{NS}}}urlset"
    locs = [el.text for el in root.iter(f"{{{NS}}}loc")]
    assert locs == ["https://x/a/", "https://x/b/"]
    assert "ns0:" not in xml


def test_render_sitemap_is_deterministic():
    locs = ["https://x/a/", "https://x/b/"]
    assert sitemap_merge.render_sitemap(locs) == sitemap_merge.render_sitemap(locs)


def test_merge_sitemaps_writes_deduped_union(tmp_path):
    _write(tmp_path / "sitemap.xml", _urlset("https://x/", "https://x/updates/"))
    _write(
        tmp_path / "updates" / "sitemap.xml",
        _urlset("https://x/updates/", "https://x/updates/2026-week-0/"),
    )

    locs = sitemap_merge.merge_sitemaps(tmp_path)

    assert locs == ["https://x/", "https://x/updates/", "https://x/updates/2026-week-0/"]
    written = (tmp_path / "sitemap.xml").read_text(encoding="utf-8")
    in_file = [el.text for el in ET.fromstring(written).iter(f"{{{NS}}}loc")]
    assert in_file == locs
    # The section sitemap is left in place, not consumed.
    assert (tmp_path / "updates" / "sitemap.xml").exists()


def test_merge_sitemaps_is_idempotent(tmp_path):
    _write(tmp_path / "sitemap.xml", _urlset("https://x/", "https://x/updates/"))
    _write(tmp_path / "updates" / "sitemap.xml", _urlset("https://x/updates/p/"))

    sitemap_merge.merge_sitemaps(tmp_path)
    first = (tmp_path / "sitemap.xml").read_text(encoding="utf-8")
    # Re-merging the merged root with its sources is a fixpoint: byte-identical.
    sitemap_merge.merge_sitemaps(tmp_path)
    assert (tmp_path / "sitemap.xml").read_text(encoding="utf-8") == first


def test_merge_sitemaps_missing_root_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        sitemap_merge.merge_sitemaps(tmp_path)
