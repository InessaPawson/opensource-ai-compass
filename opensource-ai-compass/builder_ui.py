"""Panel interface for catalog-grounded AI architecture planning."""
from __future__ import annotations

from html import escape
from io import BytesIO

import panel as pn

from catalog import Project
from system_builder import RECIPES, architecture, blueprint_json, blueprint_markdown, candidates, defaults


def build_builder(projects: list[Project]) -> pn.Column:
    """Create a session-scoped, reactive AI Stack Builder."""
    recipe_names = list(RECIPES)
    template = pn.widgets.Select(name='System blueprint', options=recipe_names, value=recipe_names[0])
    goal = pn.widgets.TextInput(name='Target outcome', placeholder='e.g. Answer support questions from internal docs')
    deployment = pn.widgets.Select(name='Where will it run?', options=['Not decided', 'On my laptop', 'Private cloud / on-prem', 'Public cloud'])
    sensitivity = pn.widgets.Select(name='Data sensitivity', options=['Not decided', 'Public', 'Internal', 'Confidential / regulated'])
    constraints = pn.widgets.TextInput(name='Constraints', placeholder='e.g. CPU-only, Python, low latency, offline')
    description = pn.pane.Markdown('')
    stage_container = pn.Column()
    selections: dict[str, pn.widgets.Select] = {}

    def rebuild_stages(event=None):
        recipe = RECIPES[template.value]
        preset = defaults(recipe, projects)
        description.object = recipe.pitch
        stage_container.clear()
        selections.clear()
        for idx, stage in enumerate(recipe.stages, 1):
            available = candidates(stage, projects)
            names = {'— Not selected —': None}
            names.update({f'{p.name} · {p.url.split("/")[-1]}': p.url for p in available})
            selection = pn.widgets.Select(name='Catalog project', options=names, value=preset.get(stage.id))
            selections[stage.id] = selection
            detail = pn.pane.Markdown('')
            def show_detail(event=None, *, widget=selection, found=available, target=detail):
                project = next((p for p in found if p.url == widget.value), None)
                target.object = (f'[{escape(project.name)}]({project.url}) — {escape(project.description)}\n\n'
                                 f'*{escape(project.area)} / {escape(project.category)} · {escape(project.status)}*') if project else ('No catalog candidate available for this stage.' if not found else 'Leave unselected if this stage needs research.')
            selection.param.watch(show_detail, 'value')
            show_detail()
            stage_container.append(pn.Card(
                pn.pane.Markdown(f'{escape(stage.description)}\n\n**Why:** {escape(stage.why)}'),
                selection, detail,
                title=f'{idx:02d} · {stage.title}', collapsed=False,
            ))
    template.param.watch(rebuild_stages, 'value')
    rebuild_stages()

    def plan():
        return architecture(template.value, projects,
                            {stage_id: widget.value for stage_id, widget in selections.items()},
                            {'goal': goal.value, 'deployment': deployment.value,
                             'data_sensitivity': sensitivity.value, 'constraints': constraints.value})

    progress = pn.indicators.Progress(name='Proposed stages', value=0, max=100)
    progress_text = pn.pane.Markdown('')
    flow = pn.pane.HTML('')
    gaps = pn.Column()
    verification = pn.Column()
    warning = pn.pane.Alert('Sensitive data selected: define a privacy/security review, retention policy and compliance requirements before using real data.', alert_type='warning', visible=False)
    preview = pn.pane.Markdown('', sizing_mode='stretch_width')
    md_download = pn.widgets.FileDownload(label='Download Markdown blueprint', filename='open-source-ai-blueprint.md', button_type='primary', callback=lambda: BytesIO(blueprint_markdown(plan()).encode('utf-8')))
    json_download = pn.widgets.FileDownload(label='Download JSON blueprint', filename='open-source-ai-blueprint.json', callback=lambda: BytesIO(blueprint_json(plan()).encode('utf-8')))

    def refresh_plan(*events):
        result = plan()
        count = sum(bool(s['tool']) for s in result['stages'])
        total = len(result['stages'])
        progress.value = round(100 * count / total) if total else 0
        progress_text.object = f'{count} of {total} stages have proposed tools — **not a readiness score**.'
        tiles = []
        for step in result['stages']:
            tiles.append('<div class="build-tile"><small>' + escape(step['stage']) +
                         '</small><strong>' + escape(step['tool'] or 'Needs selection') + '</strong></div>')
        flow.object = '<div class="build-flow">' + '<span class="build-arrow">→</span>'.join(tiles) + '</div>'
        gaps[:] = [pn.widgets.Checkbox(name=item, value=False) for item in result['gaps']]
        verification[:] = [pn.widgets.Checkbox(name=item, value=False) for item in result['verification']]
        warning.visible = sensitivity.value == 'Confidential / regulated'
        preview.object = blueprint_markdown(result)

    for widget in (goal, deployment, sensitivity, constraints):
        widget.param.watch(refresh_plan, 'value')
    def on_recipe_change(event):
        for widget in selections.values():
            widget.param.watch(refresh_plan, 'value')
        refresh_plan()
    template.param.watch(on_recipe_change, 'value')
    on_recipe_change(None)

    return pn.Column(
        '## Build an open-source AI system',
        'Choose a goal → select catalog tools → inspect architecture → export a checklist. Recommendations are examples, not tested integrations.',
        pn.Card(template, description, pn.Row(goal, deployment), pn.Row(sensitivity, constraints), title='1 · Choose what you want to build', collapsed=False),
        '### 2 · Assemble your stack', stage_container,
        '### 3 · Review the end-to-end architecture', progress, progress_text, flow,
        'Conceptual workflow, not a verified runtime dependency graph.',
        pn.Row(pn.Card(gaps, title='4 · Resolve architecture gaps'), pn.Card(verification, title='5 · Acceptance tests')),
        warning,
        pn.pane.Alert('Production requires model selection, credentials, governance, integration testing, monitoring, and operational ownership.', alert_type='info'),
        '### 6 · Export your implementation plan', pn.Row(md_download, json_download),
        pn.Accordion(('Preview the full blueprint', preview), active=[]),
        sizing_mode='stretch_width',
    )
