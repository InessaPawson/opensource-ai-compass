# Compass — Open Source AI Ecosystem Explorer

**Compass** is a standalone Python application for discovering open-source AI projects and designing illustrative AI stacks. Built with [Panel](https://panel.holoviz.org/), [HoloViews](https://holoviews.org/), and [Bokeh](https://bokeh.org/). **No Streamlit dependency.**

## Quick start (macOS / Linux)

```bash
cd ~/GitHub/opensource-ai-compass
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
panel serve app.py --show --dev
```

Open http://localhost:5006/app if the browser does not open automatically.

## Features

- **Explore Ecosystem**: reactive search/area/status filters, category bar plot, area-category heatmap, searchable project table, CSV export.
- **AI Stack Builder**: select example architecture templates, choose tools explicitly present in the catalog, inspect conceptual stages, export a Markdown or JSON blueprint.
- **Online + offline**: try the live `awesome-open-source-ai` README; fall back to the bundled starter sample after network failure. The offline sample is not the full catalog.

## Tests

```bash
python -m pip install pytest
python -m pytest -q
```

## Adding to a brand-new Git repository

Extract this ZIP. Copy **the contents of** `opensource-ai-compass/` into your new `~/GitHub/opensource-ai-compass/` directory, keeping its existing `.git` directory (do **not** copy/overwrite `.git`). For example, if you extracted the ZIP into `~/Downloads`:

```bash
rsync -av --exclude='.git' ~/Downloads/opensource-ai-compass/ ~/GitHub/opensource-ai-compass/
cd ~/GitHub/opensource-ai-compass
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
panel serve app.py --show --dev
```

## Data and project attribution

Catalog entries are credited to their linked upstream repositories. Compass reads the public source catalog at [InessaPawson/awesome-open-source-ai](https://github.com/InessaPawson/awesome-open-source-ai) when online. Bundled `data/projects.md` contains a small starting set of links, not a synced or complete archive.

These listings are not security reviews, verified technology integrations, or statements of production readiness. Review upstream licenses, provenance and maintenance status before adoption.

## Code structure

```text
app.py                Panel entry point and navigation
catalog.py            README parsing, source loading and filters
builder_ui.py         Panel architecture builder UI
system_builder.py     Framework-independent recipes and exports
ecosystem_view.py      HoloViews charts and Panel data grid
data/projects.md       Offline starter catalog
tests/                 Unit tests for parser and architecture planning
requirements.txt       Runtime dependencies
```

## License

Before distributing this new repository, confirm that you have chosen the intended license; this ZIP intentionally does not overwrite the LICENSE file already in your repository.
