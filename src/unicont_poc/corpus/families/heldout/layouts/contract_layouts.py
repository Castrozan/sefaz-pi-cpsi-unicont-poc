from __future__ import annotations

from unicont_poc.corpus.contract import DocumentDraft
from unicont_poc.corpus.families.heldout.layout_support import LayoutCatalog, Slots, draft
from unicont_poc.corpus.families.heldout.presentation import ValueFormatter, unpunctuated
from unicont_poc.domain import DocumentType

NAMED_FISCAL_SENTENCES = (
    "A fiscalização da execução ficará a cargo de {fiscal_name}.",
    "O fiscal do contrato é {fiscal_name}.",
    "FISCAL DO CONTRATO: {fiscal_name}.",
)
UNNAMED_FISCAL_SENTENCES = (
    "Este instrumento não indica nominalmente o fiscal do contrato.",
    "Não há fiscal nominalmente indicado neste contrato.",
    "FISCAL DO CONTRATO: não indicado nominalmente.",
)


def fiscal_sentence(fiscal_name: str, variant: int) -> str:
    if not fiscal_name:
        return UNNAMED_FISCAL_SENTENCES[variant]
    return NAMED_FISCAL_SENTENCES[variant].format(fiscal_name=fiscal_name)


def contract_numbered_clauses(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        f"Contrato Administrativo nº {slots['contract_number']}",
        f"CLÁUSULA PRIMEIRA - DAS PARTES: no contrato nº {slots['contract_number']}, de um lado,{slots['organ_name']} ({view.cnpj_tag(slots['organ_cnpj'])}), "
        f"doravante contratante; de outro, {view.company(slots['supplier_name'], slots['supplier_cnpj'])}, "
        f"doravante contratada.",
        f"CLÁUSULA SEGUNDA - DO OBJETO: {unpunctuated(slots['object_text'])}.",
        f"CLÁUSULA TERCEIRA - DO PREÇO: valor global de {view.money(slots['amount'])}.",
        f"CLÁUSULA QUARTA - DA VIGÊNCIA: de {view.calendar_date(slots['start_date'])} "
        f"a {view.calendar_date(slots['end_date'])}.",
        f"CLÁUSULA QUINTA - DA FISCALIZAÇÃO: {fiscal_sentence(slots['fiscal_name'], 0)}",
        f"Firmado em {view.calendar_date(slots['issue_date'])} por {slots['signer_name']}, pelo contratante.",
    )


def contract_narrative_summary(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Instrumento Contratual",
        f"Em {view.calendar_date(slots['issue_date'])}, {slots['organ_name']} celebrou o contrato nº "
        f"{slots['contract_number']} com {view.company(slots['supplier_name'], slots['supplier_cnpj'])}.",
        f"O contrato tem por objeto: {unpunctuated(slots['object_text'])}, pelo preço total de "
        f"{view.money(slots['amount'])}, e vigora de {view.calendar_date(slots['start_date'])} "
        f"até {view.calendar_date(slots['end_date'])}.",
        fiscal_sentence(slots["fiscal_name"], 1),
        f"Assinou pelo contratante: {slots['signer_name']}.",
    )


def contract_tabular_summary(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Resumo do Contrato",
        f"CONTRATO Nº {slots['contract_number']} | ASSINATURA {view.calendar_date(slots['issue_date'])} | "
        f"SIGNATÁRIO: {slots['signer_name']}",
        f"CONTRATANTE: {slots['organ_name']} | CONTRATADA: {slots['supplier_name']} | "
        f"{view.cnpj_tag(slots['supplier_cnpj'])}",
        f"OBJETO: {unpunctuated(slots['object_text'])}",
        f"VALOR GLOBAL: {view.money(slots['amount'])} | PRAZO: {view.calendar_date(slots['start_date'])} "
        f"a {view.calendar_date(slots['end_date'])}",
        fiscal_sentence(slots["fiscal_name"], 2),
    )


CONTRACT_LAYOUTS: LayoutCatalog = {
    DocumentType.CONTRATO: (contract_numbered_clauses, contract_narrative_summary, contract_tabular_summary),
}
