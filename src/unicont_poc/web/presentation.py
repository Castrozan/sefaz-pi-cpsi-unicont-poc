from __future__ import annotations

import re
from decimal import Decimal
from markupsafe import Markup, escape

from unicont_poc.corpus.formatting import brazilian_money
from unicont_poc.domain import CATEGORY_LABELS, DOCUMENT_TYPE_LABELS, DocumentType, ProcessCategory

STATUS_LABELS = {
    "conforme": "Conforme",
    "nao_conforme": "Não conforme",
    "nao_verificavel": "Conferência humana",
    "prejudicado": "Prejudicado",
}
RISK_LABELS = {"baixo": "Baixo", "medio": "Médio", "alto": "Alto"}
VERDICT_LABELS = {
    "conforme": "Sem apontamentos",
    "nao_conforme": "Com apontamentos",
    "revisao_humana": "Conferência humana",
}
REVIEW_LABELS = {
    "aguardando_analista": "Aguardando analista",
    "aprovado": "Aprovado pelo analista",
    "devolvido": "Devolvido pelo analista",
}


def money_label(value: object) -> str:
    return "—" if value is None else brazilian_money(Decimal(str(value)))


def category_label(value: str) -> str:
    return CATEGORY_LABELS[ProcessCategory(value)]


def document_type_label(value: str) -> str:
    return DOCUMENT_TYPE_LABELS[DocumentType(value)]


def percent_label(value: float | None) -> str:
    return "—" if value is None else f"{value * 100:.1f}%".replace(".", ",")


def highlighted_snippet(snippet: str | None) -> Markup:
    escaped = str(escape(snippet or ""))
    return Markup(escaped.replace("[[", "<mark>").replace("]]", "</mark>"))


def highlighted_page(text: str, quote: str) -> Markup:
    if not quote:
        return escape(text)
    pieces = re.split(f"({re.escape(quote)})", text, maxsplit=1, flags=re.IGNORECASE)
    if len(pieces) < 3:
        return escape(text)
    return Markup(f'{escape(pieces[0])}<mark id="citacao">{escape(pieces[1])}</mark>{escape(pieces[2])}')
