from __future__ import annotations

from unicont_poc.corpus.contract import DocumentDraft
from unicont_poc.corpus.families.heldout.layout_support import LayoutCatalog, Slots, draft
from unicont_poc.corpus.families.heldout.presentation import ValueFormatter, unpunctuated
from unicont_poc.domain import DocumentType


def ordinance_articulated(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        f"Portaria nº {slots['ordinance_number']}",
        f"PORTARIA Nº {slots['ordinance_number']}, DE {view.calendar_date(slots['issue_date'])}.",
        "O responsável pela unidade, no uso de suas atribuições, RESOLVE:",
        f"Art. 1º Designar {slots['fiscal_name']} como fiscal do contrato nº {slots['contract_number']}.",
        "Art. 2º Esta portaria entra em vigor na data de sua assinatura.",
        f"{slots['signer_name']}.",
    )


def ordinance_narrative(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Ato de Designação de Fiscal",
        f"Por meio da portaria nº {slots['ordinance_number']}, datada de {view.calendar_date(slots['issue_date'])}, "
        f"{slots['signer_name']} designa {slots['fiscal_name']} para atuar como fiscal do contrato nº "
        f"{slots['contract_number']}, ficando incumbido(a) de acompanhar e fiscalizar sua execução.",
    )


def ordinance_tabular(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Designação de Fiscal de Contrato",
        f"PORTARIA | Nº {slots['ordinance_number']} | DATA {view.calendar_date(slots['issue_date'])}",
        f"FISCAL DESIGNADO | {slots['fiscal_name']}",
        f"CONTRATO FISCALIZADO | {slots['contract_number']}",
        f"AUTORIDADE SIGNATÁRIA | {slots['signer_name']}",
    )


def technical_responsibility_form(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        f"Anotação de Responsabilidade Técnica - ART nº {slots['art_number']}",
        f"Responsável técnico: {slots['responsible_name']}, registro profissional nº {slots['registration_number']}.",
        f"Objeto da anotação de responsabilidade técnica: {unpunctuated(slots['description'])}.",
        f"ART nº {slots['art_number']} registrada em {view.calendar_date(slots['issue_date'])}.",
    )


def technical_responsibility_narrative(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Registro de Responsabilidade Técnica",
        f"Nos termos da legislação profissional, {slots['responsible_name']}, registro nº "
        f"{slots['registration_number']}, assume a responsabilidade técnica pelo seguinte trabalho: "
        f"{unpunctuated(slots['description'])}.",
        f"A anotação de responsabilidade técnica (ART nº {slots['art_number']}) foi registrada em "
        f"{view.calendar_date(slots['issue_date'])}.",
    )


def technical_responsibility_tabular(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "ART",
        f"ART Nº | {slots['art_number']} | ANOTAÇÃO DE RESPONSABILIDADE TÉCNICA",
        f"PROFISSIONAL | {slots['responsible_name']} | REGISTRO {slots['registration_number']}",
        f"ATIVIDADE TÉCNICA | {unpunctuated(slots['description'])}",
        f"DATA DE REGISTRO | {view.calendar_date(slots['issue_date'])}",
    )


DESIGNATION_LAYOUTS: LayoutCatalog = {
    DocumentType.PORTARIA_FISCAL: (ordinance_articulated, ordinance_narrative, ordinance_tabular),
    DocumentType.ART: (
        technical_responsibility_form,
        technical_responsibility_narrative,
        technical_responsibility_tabular,
    ),
}
