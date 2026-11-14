"""Open Source AI Compass — Panel + HoloViews.

Run: panel serve app.py --show --dev
"""
from __future__ import annotations

import panel as pn
import holoviews as hv

from catalog import REPO, parse_projects, read_readme
from builder_ui import build_builder
from ecosystem_view import build_explorer

pn.extension('tabulator', sizing_mode='stretch_width')
hv.extension('bokeh', logo=False)

STYLE = '''
:root {--navy:#082B80;--blue:#5275F7;--ink:#172549}
body {background:#F7F9FE}
.hero {padding:28px 32px;border-radius:18px;background:linear-gradient(110deg,#082B80,#19469D 60%,#5275F7);color:white;margin-bottom:18px}
.hero h1 {color:white;margin:0 0 8px;font-size:2.25rem}.hero p{color:#E1E9FF;margin:0}
.build-flow{display:flex;align-items:stretch;gap:8px;flex-wrap:wrap;margin:14px 0}
.build-tile{flex:1 1 135px;min-width:135px;min-height:70px;padding:12px;border-radius:12px;background:white;border:1px solid #CDD9F3;display:flex;flex-direction:column;gap:8px}
.build-tile small{color:#5C6A88}.build-tile strong{color:#082B80;overflow-wrap:anywhere}
.build-arrow{align-self:center;color:#5275F7}
'''


def create_app() -> pn.template.FastListTemplate:
    """Called per browser session; avoid sharing interactive widget state."""
    markdown, provenance = read_readme(live=True)
    projects = parse_projects(markdown)
    builder = build_builder(projects)
    explorer = build_explorer(projects)
    hero = pn.pane.HTML('''<div class="hero"><h1>Compass</h1>
    <p>Design a blueprint for your AI stack with open-source tools.</p></div>''')
    tabs = pn.Tabs(('AI Stack Builder', builder), ('Explore ecosystem', explorer), dynamic=True)
    footer = pn.pane.Markdown(f'Catalog: **{provenance}** · Listings are not endorsements or security assessments.  '
                              f'[Catalog on GitHub]({REPO}) · Built with Python, Panel and HoloViews.')
    return pn.template.FastListTemplate(
        title='Compass | Open Source AI', site='Compass',
        main=[hero, tabs, footer],
        raw_css=[STYLE], accent_base_color='#5275F7',
        header_background='#082B80',
    )


create_app().servable()
