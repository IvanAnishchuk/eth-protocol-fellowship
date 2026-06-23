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


def test_extract_graph_types_handles_list_type():
    html = (
        '<script type="application/ld+json">'
        '{"@graph":[{"@type":["BlogPosting","Article"]}]}'
        "</script>"
    )
    assert check_jsonld.extract_graph_types(html) == {"BlogPosting", "Article"}


def test_extract_graph_types_reads_single_node():
    html = (
        '<script type="application/ld+json">'
        '{"@context":"https://schema.org","@type":"WebSite"}'
        "</script>"
    )
    assert check_jsonld.extract_graph_types(html) == {"WebSite"}


def test_extract_graph_types_tolerates_markup_variations():
    html = (
        "<script nonce=\"r4nd0m\" type='application/ld+json'>"
        '{"@graph":[{"@type":"Person"}]}'
        "</script>"
    )
    assert check_jsonld.extract_graph_types(html) == {"Person"}
