import json
from catalog import read_readme, parse_projects
from system_builder import RECIPES, architecture, blueprint_json, blueprint_markdown, defaults


def test_recipes_generate_exportable_plans():
    projects = parse_projects(read_readme(live=False)[0])
    for key, recipe in RECIPES.items():
        plan = architecture(key, projects, defaults(recipe, projects), {'goal': 'Demo'})
        assert len(plan['stages']) == len(recipe.stages)
        assert json.loads(blueprint_json(plan))['name'] == key
        assert '# ' + key in blueprint_markdown(plan)


def test_invalid_selection_is_not_accepted():
    projects = parse_projects(read_readme(live=False)[0])
    plan = architecture('Local private assistant', projects, {'model': 'https://github.com/untrusted/repo'}, {})
    assert plan['stages'][0]['tool'] is None
