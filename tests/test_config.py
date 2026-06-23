import _config


def test_check_site_url_accepts_absolute_with_trailing_slash():
    assert _config.check_site_url("https://example.com/site/") == []


def test_check_site_url_flags_missing_trailing_slash():
    problems = _config.check_site_url("https://example.com/site")
    assert any("end with '/'" in p for p in problems)


def test_check_site_url_flags_relative_url():
    problems = _config.check_site_url("/eth-protocol-fellowship/")
    assert any("absolute" in p for p in problems)


def test_check_site_url_flags_non_string():
    problems = _config.check_site_url(["https://example.com/"])
    assert problems
    assert "string" in problems[0]


def test_check_site_url_flags_missing_host():
    problems = _config.check_site_url("https://")
    assert any("absolute URL" in p for p in problems)


def test_site_url_from_config_reads_value(tmp_path):
    cfg = tmp_path / "zensical.toml"
    cfg.write_text('[project]\nsite_url = "https://example.com/x/"\n', encoding="utf-8")
    assert _config.site_url_from_config(cfg) == "https://example.com/x/"


def test_site_url_problems_clean_on_valid_config(tmp_path):
    cfg = tmp_path / "zensical.toml"
    cfg.write_text('[project]\nsite_url = "https://example.com/x/"\n', encoding="utf-8")
    assert _config.site_url_problems(cfg) == []


def test_site_url_problems_reports_missing_key_without_crashing(tmp_path):
    cfg = tmp_path / "zensical.toml"
    cfg.write_text('[project]\nsite_name = "x"\n', encoding="utf-8")
    problems = _config.site_url_problems(cfg)
    assert problems
    assert "site_url" in problems[0]


def test_site_url_problems_reports_missing_file_without_crashing(tmp_path):
    problems = _config.site_url_problems(tmp_path / "nope.toml")
    assert problems


def test_site_url_problems_reports_invalid_utf8_without_crashing(tmp_path):
    cfg = tmp_path / "zensical.toml"
    cfg.write_bytes(b"\xff\xfe\x00")
    problems = _config.site_url_problems(cfg)
    assert problems
    assert "UTF-8" in problems[0]
