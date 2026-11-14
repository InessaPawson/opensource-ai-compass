from catalog import Project, parse_projects, read_readme, search_projects


def test_offline_catalog():
    body, provenance = read_readme(live=False)
    items = parse_projects(body)
    assert len(items) >= 15
    assert 'Bundled' in provenance
    assert len({p.url for p in items}) == len(items)


def test_search_filters_and_empty_lists():
    items = [Project('A', 'https://example.org/a', 'hi', 'Foundation', 'Models', 'Listed'),
             Project('B', 'https://example.org/b', 'bye', 'Security', 'Tools', 'Archived')]
    assert [p.name for p in search_projects(items, 'hi')] == ['A']
    assert search_projects(items, areas=[]) == []
    assert [p.name for p in search_projects(items, statuses=['Archived'])] == ['B']


def test_duplicates_ignored():
    raw = '## Area\n### Category\n- [A](https://example.org/a) - Hello\n- [B](https://example.org/a) - Duplicate'
    assert len(parse_projects(raw)) == 1
