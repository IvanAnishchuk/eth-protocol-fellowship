import pytest

import check_jsonld


def test_extract_graph_types_collects_all():
    html = (
        "<head>"
        '<script type="application/ld+json">'
        '{"@context":"https://schema.org","@graph":'
        '[{"@type":"BlogPosting"},{"@type":"BreadcrumbList"}]}'
        "</script></head>"
    )
    assert check_jsonld.extract_graph_types(html) == {"BlogPosting", "BreadcrumbList"}


def test_extract_graph_types_malformed_raises():
    html = '<script type="application/ld+json">{not json}</script>'
    with pytest.raises(ValueError):
        check_jsonld.extract_graph_types(html)


def test_extract_graph_types_ignores_non_dict_blocks():
    html = '<script type="application/ld+json">[1, 2, 3]</script>'
    assert check_jsonld.extract_graph_types(html) == set()
