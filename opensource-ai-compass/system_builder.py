"""Deterministic, catalog-grounded AI stack planning.

These recipes illustrate potential stacks; selections are not compatibility,
security, deployment, or performance endorsements.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

from catalog import Project


@dataclass(frozen=True)
class Stage:
    id: str
    title: str
    description: str
    why: str
    repo_urls: tuple[str, ...]
    optional: bool = False


@dataclass(frozen=True)
class Recipe:
    title: str
    pitch: str
    stages: tuple[Stage, ...]
    gaps: tuple[str, ...]
    tests: tuple[str, ...]


def stage(id: str, title: str, description: str, why: str, *repos: str, optional: bool = False) -> Stage:
    return Stage(id, title, description, why, tuple(f'https://github.com/{repo}' for repo in repos), optional)


RECIPES: dict[str, Recipe] = {
    'Local private assistant': Recipe(
        'Local private assistant', 'Prototype a local-first assistant on hardware you control.',
        (
            stage('model', 'Model utilities', 'Load and transform model artifacts', 'Prepare input and model interfaces', 'huggingface/transformers'),
            stage('inference', 'Local inference', 'Serve a model on local hardware', 'Keep inference within a defined network boundary', 'ggml-org/llama.cpp'),
            stage('interface', 'Prototyping UI', 'Experiment with prompts and workflows', 'Test user interactions', 'marimo-team/marimo', 'jupyterlab/jupyter-ai'),
            stage('security', 'Input and output checks', 'Evaluate dangerous inputs and outputs', 'Reduce avoidable risks', 'protectai/llm-guard', 'NVIDIA/garak'),
            stage('evaluation', 'Evaluation suite', 'Measure assistant quality', 'Check answers before deployment', 'confident-ai/deepeval'),
            stage('deployment', 'Packaging', 'Optionally package the model service', 'Enable repeatable execution', 'bentoml/BentoML', optional=True),
        ),
        ('Choose weights and confirm model license, device memory, and CPU/GPU support.',
         'Review logs, telemetry, data retention, and outbound network access.',
         'Build and test a user-facing interface separately.'),
        ('Test offline operation on the target device.', 'Benchmark response latency and memory.',
         'Check sensitive input and output handling.'),
    ),
    'Tool-using AI agent': Recipe(
        'Tool-using AI agent', 'Design an agent that calls tools under explicit authorization.',
        (
            stage('model', 'Model interface', 'Integrate the foundation model', 'Provide model access', 'huggingface/transformers'),
            stage('orchestration', 'Agent orchestration', 'Coordinate state and tool execution', 'Control task flow and approvals', 'langchain-ai/langgraph', 'pydantic/pydantic-ai'),
            stage('inference', 'Model serving', 'Host your model API', 'Keep serving independently scalable', 'vllm-project/vllm'),
            stage('security', 'Adversarial testing', 'Probe prompts and tool boundaries', 'Reduce prompt-injection risks', 'NVIDIA/garak', 'Azure/PyRIT'),
            stage('evaluation', 'Agent evaluation', 'Measure task completion and recovery', 'Detect regressions', 'confident-ai/deepeval'),
            stage('deployment', 'Runtime', 'Run the agent service', 'Repeatable production operation', 'bentoml/BentoML', 'ray-project/ray'),
        ),
        ('Define least-privilege credentials and tool permission scopes.',
         'Require approval for destructive or externally visible tool actions.',
         'Specify retry, timeout, audit logging, and rollback policies.'),
        ('Test malicious tool responses and prompt injection.', 'Test a denied permission request.',
         'Test partial failure and idempotent retries.'),
    ),
    'Document question answering (RAG)': Recipe(
        'Document question answering (RAG)', 'Build a retrieval-augmented question-answering prototype.',
        (
            stage('ingestion', 'Document ingestion', 'Read and preprocess documents', 'Build retrievable content', 'langchain-ai/langchain'),
            stage('embedding', 'Embedding model', 'Represent documents and queries', 'Enable semantic retrieval', 'UKPLab/sentence-transformers'),
            stage('index', 'Vector index', 'Index embeddings', 'Retrieve candidates', 'chroma-core/chroma', 'qdrant/qdrant'),
            stage('inference', 'Model serving', 'Generate grounded answers', 'Use retrieved context for answers', 'vllm-project/vllm', 'ggml-org/llama.cpp'),
            stage('evaluation', 'Quality evaluation', 'Check grounding and answer quality', 'Detect hallucination and retrieval failures', 'explodinggradients/ragas', 'confident-ai/deepeval'),
            stage('security', 'Security review', 'Check prompt and document injection handling', 'Control untrusted text', 'protectai/llm-guard'),
        ),
        ('Define document access controls and update/deletion processes.',
         'Verify embedding dimensions, API versions, and license compatibility.',
         'Add citations and permission-aware retrieval to the application.'),
        ('Verify no document outside user permissions is retrieved.',
         'Measure retrieval precision on representative questions.',
         'Test stale document updates and prompt-injection content.'),
    ),
}


def candidates(step: Stage, projects: list[Project]) -> list[Project]:
    """Only explicitly named repo candidates are offered; no inferred integrations."""
    by_url = {p.url.rstrip('/').casefold(): p for p in projects}
    return [by_url[url.casefold()] for url in step.repo_urls if url.casefold() in by_url]


def defaults(recipe: Recipe, projects: list[Project]) -> dict[str, str | None]:
    return {step.id: (candidates(step, projects)[0].url if candidates(step, projects) else None)
            for step in recipe.stages}


def architecture(recipe_name: str, projects: list[Project], selected: dict[str, str | None],
                 context: dict[str, str]) -> dict[str, Any]:
    recipe = RECIPES[recipe_name]
    entries = []
    for step in recipe.stages:
        chosen = next((p for p in candidates(step, projects) if p.url == selected.get(step.id)), None)
        entries.append({'id': step.id, 'stage': step.title, 'why': step.why,
                        'tool': chosen.name if chosen else None, 'url': chosen.url if chosen else None,
                        'optional': step.optional})
    missing = [f'Select a catalog tool for {row["stage"]}.' for row in entries
               if not row['tool'] and not row['optional']]
    return {'name': recipe.title, 'pitch': recipe.pitch, 'context': dict(context), 'stages': entries,
            'gaps': list(recipe.gaps) + missing, 'verification': list(recipe.tests),
            'disclaimer': 'Illustrative planning only; compatibility, security, and production readiness are unverified.'}


def blueprint_markdown(plan: dict[str, Any]) -> str:
    lines = [f'# {plan["name"]}', '', plan['pitch'], '', f'> {plan["disclaimer"]}', '', '## Constraints', '']
    for key, value in plan['context'].items():
        lines.append(f'- **{key.replace("_", " ").title()}:** {value or "Not specified"}')
    lines.extend(['', '## Proposed stages', ''])
    for row in plan['stages']:
        selection = f'[{row["tool"]}]({row["url"]})' if row['tool'] else 'Needs selection'
        lines.append(f'- **{row["stage"]}** — {selection}. {row["why"]}')
    for title, key in [('Open gaps', 'gaps'), ('Acceptance tests', 'verification')]:
        lines.extend(['', f'## {title}', ''])
        lines.extend(f'- [ ] {item}' for item in plan[key])
    return '\n'.join(lines) + '\n'


def blueprint_json(plan: dict[str, Any]) -> str:
    return json.dumps(plan, ensure_ascii=False, indent=2) + '\n'
