"""Load a curated catalog from the original awesome list, with offline fallback.

This code lives in Open Source AI Compass; it does not require cloning another repository.
Remote downloads are explicitly bounded by a timeout and validated.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import requests

REPO = 'https://github.com/openteams-ai/awesome-open-source-ai'
RAW = 'https://raw.githubusercontent.com/openteams-ai/awesome-open-source-ai/main/README.md'
LOCAL = Path(__file__).parent / 'data' / 'projects.md'


@dataclass(frozen=True)
class Project:
    name: str
    url: str
    description: str
    area: str
    category: str
    status: str


def read_readme(live: bool = True) -> tuple[str, str]:
    """Return live upstream README if reachable; otherwise use bundled samples."""
    if live:
        try:
            resp = requests.get(RAW, timeout=8, headers={'User-Agent': 'open-source-ai-compass/0.1'})
            resp.raise_for_status()
            if len(resp.content) < 4_000_000 and '## Foundations' in resp.text:
                return resp.text, 'Live upstream catalog'
        except requests.RequestException:
            pass
    return LOCAL.read_text(encoding='utf-8'), 'Bundled starter catalog (offline fallback)'


def parse_projects(markdown: str) -> list[Project]:
    """Parse Markdown lists with ## areas and ### categories."""
    area, category = '', ''
    projects: list[Project] = []
    seen: set[str] = set()
    link = re.compile(r'^\s*[-*]\s+\[([^\]]+)\]\((https?://[^)]+)\)\s*(?:[-–—:]\s*)?(.*)$')
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if line.startswith('## '):
            area = re.sub(r'\s+#+$', '', line[3:]).strip()
            category = ''
        elif line.startswith('### '):
            category = re.sub(r'\s+#+$', '', line[4:]).strip()
        elif area and category:
            match = link.match(line)
            if not match:
                continue
            name, url, description = match.groups()
            url = url.strip()
            if url in seen:
                continue
            seen.add(url)
            desc = re.sub(r'\s+', ' ', description).strip()
            status = ('Archived' if re.search(r'\barchived\b', desc, re.I)
                      else 'Inactive' if re.search(r'not actively maintained|development wound down', desc, re.I)
                      else 'Listed')
            projects.append(Project(name.strip(), url, desc, area, category, status))
    return projects


def search_projects(projects: list[Project], query: str = '', areas: list[str] | None = None,
                    categories: list[str] | None = None, statuses: list[str] | None = None) -> list[Project]:
    terms = query.casefold().split()
    return [p for p in projects
            if (areas is None or p.area in areas)
            and (categories is None or p.category in categories)
            and (statuses is None or p.status in statuses)
            and all(term in f'{p.name} {p.description} {p.area} {p.category}'.casefold() for term in terms)]
