from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from unicont_poc.web import presentation
from unicont_poc.web.routes import Routes

TEMPLATE_DIRECTORY = Path(__file__).parent / "templates"


def build_template_environment(routes: Routes, static_site: bool = False) -> Environment:
    environment = Environment(loader=FileSystemLoader(TEMPLATE_DIRECTORY), autoescape=select_autoescape())
    environment.filters.update(
        money=presentation.money_label,
        category=presentation.category_label,
        document_type=presentation.document_type_label,
        percent=presentation.percent_label,
        score=presentation.score_label,
        snippet=presentation.highlighted_snippet,
    )
    environment.globals.update(
        routes=routes,
        static_site=static_site,
        status_labels=presentation.STATUS_LABELS,
        risk_labels=presentation.RISK_LABELS,
        verdict_labels=presentation.VERDICT_LABELS,
        review_labels=presentation.REVIEW_LABELS,
        group_labels=presentation.GROUP_LABELS,
    )
    return environment
