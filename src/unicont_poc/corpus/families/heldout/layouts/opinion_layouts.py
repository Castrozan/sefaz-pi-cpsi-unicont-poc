from __future__ import annotations

from unicont_poc.corpus.contract import DocumentDraft
from unicont_poc.corpus.families.heldout.categorical_statements import opinion_conclusion
from unicont_poc.corpus.families.heldout.layout_support import LayoutCatalog, Slots, draft
from unicont_poc.corpus.families.heldout.presentation import ValueFormatter
from unicont_poc.domain import DocumentType


def opinion_sectioned(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    conclusion = opinion_conclusion(slots["opinion_kind"], slots["opinion_detail"], 0)
    return draft(
        f"Parecer Jurídico nº {slots['opinion_number']}",
        f"PARECER JURÍDICO Nº {slots['opinion_number']}, emitido em {view.calendar_date(slots['issue_date'])}.",
        "I - Relatório: o processo foi submetido à análise da assessoria jurídica.",
        f"II - Conclusão: {conclusion}.",
        f"{slots['signer_name']}, parecerista.",
    )


def opinion_narrative(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    conclusion = opinion_conclusion(slots["opinion_kind"], slots["opinion_detail"], 1)
    return draft(
        "Manifestação da Assessoria Jurídica",
        f"Em {view.calendar_date(slots['issue_date'])}, {slots['signer_name']} emitiu o parecer jurídico nº "
        f"{slots['opinion_number']} sobre o presente processo.",
        f"Ante o exposto, {conclusion}.",
    )


def opinion_conclusion_first(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    conclusion = opinion_conclusion(slots["opinion_kind"], slots["opinion_detail"], 2)
    return draft(
        "Parecer",
        f"Em síntese, {conclusion}.",
        f"Trata-se do parecer jurídico nº {slots['opinion_number']}, assinado por {slots['signer_name']} em "
        f"{view.calendar_date(slots['issue_date'])}.",
    )


OPINION_LAYOUTS: LayoutCatalog = {
    DocumentType.PARECER_JURIDICO: (opinion_sectioned, opinion_narrative, opinion_conclusion_first),
}
