from __future__ import annotations

from unicont_poc.corpus.contract import DocumentDraft
from unicont_poc.corpus.families.heldout.layout_support import LayoutCatalog, Slots, draft
from unicont_poc.corpus.families.heldout.presentation import ValueFormatter, unpunctuated
from unicont_poc.domain import DocumentType


def agreement_numbered_clauses(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        f"Termo de Convênio nº {slots['agreement_number']}",
        f"CLÁUSULA 1ª - DOS PARTÍCIPES: no convênio nº {slots['agreement_number']}, {slots['organ_name']} ({view.cnpj_tag(slots['organ_cnpj'])}), como "
        f"concedente, e {view.company(slots['partner_name'], slots['partner_cnpj'])}, como convenente.",
        f"CLÁUSULA 2ª - DO OBJETO: {unpunctuated(slots['object_text'])}.",
        f"CLÁUSULA 3ª - DOS RECURSOS: valor global de {view.money(slots['amount'])}.",
        f"CLÁUSULA 4ª - DA VIGÊNCIA: de {view.calendar_date(slots['start_date'])} "
        f"a {view.calendar_date(slots['end_date'])}.",
        f"CLÁUSULA 5ª - DA PRESTAÇÃO DE CONTAS: até {view.calendar_date(slots['report_deadline'])}.",
        f"Firmado em {view.calendar_date(slots['issue_date'])} por {slots['signer_name']}.",
    )


def agreement_narrative(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Instrumento de Convênio",
        f"Em {view.calendar_date(slots['issue_date'])}, {slots['organ_name']} celebrou, como concedente, o convênio "
        f"nº {slots['agreement_number']} com {view.company(slots['partner_name'], slots['partner_cnpj'])}.",
        f"O convênio visa ao seguinte objeto: {unpunctuated(slots['object_text'])}. Os recursos somam "
        f"{view.money(slots['amount'])} e a vigência vai de {view.calendar_date(slots['start_date'])} "
        f"até {view.calendar_date(slots['end_date'])}.",
        f"A prestação de contas deve ser apresentada até {view.calendar_date(slots['report_deadline'])}. "
        f"Assinatura: {slots['signer_name']}.",
    )


def agreement_tabular_summary(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Ficha-Resumo do Convênio",
        f"TERMO DE CONVÊNIO Nº {slots['agreement_number']} | ASSINADO EM {view.calendar_date(slots['issue_date'])} "
        f"POR {slots['signer_name']}",
        f"CONCEDENTE: {slots['organ_name']} | CONVENENTE: {slots['partner_name']} | "
        f"{view.cnpj_tag(slots['partner_cnpj'])}",
        f"OBJETO: {unpunctuated(slots['object_text'])}",
        f"VALOR: {view.money(slots['amount'])} | VIGÊNCIA: {view.calendar_date(slots['start_date'])} "
        f"a {view.calendar_date(slots['end_date'])}",
        f"PRAZO PARA PRESTAR CONTAS: {view.calendar_date(slots['report_deadline'])}",
    )


def work_plan_itemized(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    items = [f"- {unpunctuated(item)}" for item in slots["allowed_items"]]
    return draft(
        "Plano de Trabalho",
        f"Plano de trabalho vinculado ao convênio nº {slots['agreement_number']}, apresentado por "
        f"{slots['partner_name']} em {view.calendar_date(slots['issue_date'])}.",
        f"Objeto: {unpunctuated(slots['object_text'])}.",
        "Itens de despesa admitidos:",
        *items,
        f"Valor total do plano: {view.money(slots['amount'])}.",
    )


def work_plan_narrative(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    items = "; ".join(unpunctuated(item) for item in slots["allowed_items"])
    return draft(
        "Detalhamento da Execução",
        f"Este plano de trabalho, de {view.calendar_date(slots['issue_date'])}, integra o convênio nº "
        f"{slots['agreement_number']} firmado com {slots['partner_name']}, para o objeto: "
        f"{unpunctuated(slots['object_text'])}.",
        f"Somente podem ser pagas despesas dos seguintes tipos: {items}. O montante previsto é de "
        f"{view.money(slots['amount'])}.",
    )


def work_plan_tabular(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    items = " / ".join(unpunctuated(item) for item in slots["allowed_items"])
    return draft(
        "Plano de Aplicação dos Recursos",
        f"PLANO DE TRABALHO | CONVÊNIO Nº {slots['agreement_number']} | {slots['partner_name']}",
        f"OBJETO | {unpunctuated(slots['object_text'])}",
        f"ITENS DE DESPESA AUTORIZADOS | {items}",
        f"VALOR TOTAL | {view.money(slots['amount'])} | DATA {view.calendar_date(slots['issue_date'])}",
    )


def execution_report_formal(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    partner = view.company(slots["partner_name"], slots["partner_cnpj"])
    return draft(
        "Relatório de Execução do Objeto",
        f"Relatório de execução do convênio nº {slots['agreement_number']}, apresentado por {partner}.",
        f"Objeto executado: {unpunctuated(slots['object_text'])}.",
        f"Elaborado em {view.calendar_date(slots['issue_date'])} por {slots['signer_name']} e entregue em "
        f"{view.calendar_date(slots['delivered_on'])}.",
    )


def execution_report_narrative(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Prestação de Informações sobre a Execução",
        f"Este relatório de execução, entregue em {view.calendar_date(slots['delivered_on'])}, informa a realização "
        f"do objeto do convênio nº {slots['agreement_number']}: {unpunctuated(slots['object_text'])}.",
        f"Foi redigido por {slots['signer_name']}, em nome de {slots['partner_name']} "
        f"({view.cnpj_tag(slots['partner_cnpj'])}), com data de {view.calendar_date(slots['issue_date'])}.",
    )


def execution_report_tabular(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Relatório Final do Convênio",
        f"RELATÓRIO DE EXECUÇÃO | CONVÊNIO Nº {slots['agreement_number']}",
        f"CONVENENTE | {slots['partner_name']} | {view.cnpj_tag(slots['partner_cnpj'])}",
        f"OBJETO REALIZADO | {unpunctuated(slots['object_text'])}",
        f"RESPONSÁVEL | {slots['signer_name']} | DATA {view.calendar_date(slots['issue_date'])} | "
        f"ENTREGA {view.calendar_date(slots['delivered_on'])}",
    )


AGREEMENT_LAYOUTS: LayoutCatalog = {
    DocumentType.TERMO_CONVENIO: (agreement_numbered_clauses, agreement_narrative, agreement_tabular_summary),
    DocumentType.PLANO_TRABALHO: (work_plan_itemized, work_plan_narrative, work_plan_tabular),
    DocumentType.RELATORIO_EXECUCAO: (execution_report_formal, execution_report_narrative, execution_report_tabular),
}
