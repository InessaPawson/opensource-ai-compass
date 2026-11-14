"""Reactive HoloViews catalog explorer rendered natively by Panel."""
from __future__ import annotations

from collections import Counter
from io import BytesIO
from typing import Sequence

import holoviews as hv
import pandas as pd
import panel as pn

from catalog import Project, search_projects


def category_counts(projects: Sequence[Project]) -> list[tuple[str, int]]:
    counts = Counter(p.category for p in projects)
    return sorted(counts.items(), key=lambda item: (-item[1], item[0].casefold()))


def area_category_counts(projects: Sequence[Project]) -> list[tuple[str, str, int]]:
    counts = Counter((p.area, p.category) for p in projects)
    return [(area, cat, count) for (area, cat), count in sorted(counts.items())]


def projects_frame(projects: Sequence[Project]) -> pd.DataFrame:
    return pd.DataFrame([{'Project': p.name, 'Area': p.area, 'Category': p.category,
                          'Status': p.status, 'Description': p.description,
                          'Repository': p.url} for p in projects],
                        columns=['Project', 'Area', 'Category', 'Status', 'Description', 'Repository'])


def build_explorer(projects: list[Project]) -> pn.Column:
    """Build filters and live Bokeh-backed plots with no HTML embedding."""
    search = pn.widgets.TextInput(name='Search', placeholder='Project, category or description')
    areas = pn.widgets.MultiChoice(name='Areas', options=sorted({p.area for p in projects}), value=sorted({p.area for p in projects}))
    statuses = pn.widgets.MultiChoice(name='Listing status', options=sorted({p.status for p in projects}), value=sorted({p.status for p in projects}))

    def filtered(query, selected_areas, selected_statuses):
        if not selected_areas or not selected_statuses:
            return []
        return search_projects(projects, query=query, areas=selected_areas, statuses=selected_statuses)

    view = pn.bind(filtered, search, areas, statuses)

    def summary(items):
        return f'### {len(items)} matching projects'

    def charts(items):
        if not items:
            return pn.pane.Alert('No projects match the current filters.', alert_type='info')
        top = category_counts(items)[:15]
        bars = hv.Bars(top, kdims=['Category'], vdims=['Projects']).opts(
            title='Listings by category (top 15)', height=420, responsive=True,
            color='#5275F7', tools=['hover'], xrotation=45, show_grid=True)
        visible = {category for category, _ in top}
        pairs = [(area, category, count) for area, category, count in area_category_counts(items) if category in visible]
        if len({a for a, _, _ in pairs}) > 1 and len({c for _, c, _ in pairs}) > 1:
            heatmap = hv.HeatMap(pairs, kdims=['Area', 'Category'], vdims=['Projects']).opts(
                title='Area / category breakdown', height=420, responsive=True,
                cmap='Blues', colorbar=True, tools=['hover'], xrotation=45)
            return pn.Column(pn.pane.HoloViews(bars), pn.pane.HoloViews(heatmap))
        return pn.pane.HoloViews(bars)

    def table(items):
        return pn.widgets.Tabulator(projects_frame(items), show_index=False, pagination='local', page_size=15,
                                    formatters={'Repository': {'type': 'link', 'urlField': 'Repository'}},
                                    sizing_mode='stretch_width', disabled=True)

    download = pn.widgets.FileDownload(
        label='Download filtered catalog (CSV)', filename='open-source-ai-catalog.csv',
        callback=lambda: BytesIO(projects_frame(filtered(search.value, areas.value, statuses.value)).to_csv(index=False).encode('utf-8')))
    return pn.Column(
        '## Explore the open-source AI ecosystem',
        'Counts represent README listings, not adoption, integration compatibility, quality or security.',
        pn.Row(search, areas, statuses),
        pn.bind(summary, view), pn.bind(charts, view),
        '### Project directory', pn.bind(table, view), download,
        sizing_mode='stretch_width',
    )
