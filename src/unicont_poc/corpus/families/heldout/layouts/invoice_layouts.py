from __future__ import annotations

from unicont_poc.corpus.contract import DocumentDraft
from unicont_poc.corpus.families.heldout.categorical_statements import attestation_statement
from unicont_poc.corpus.families.heldout.layout_support import LayoutCatalog, Slots, draft
from unicont_poc.corpus.families.heldout.presentation import ValueFormatter, unpunctuated
from unicont_poc.domain import DocumentType


def invoice_formal_prose(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    supplier = view.company(slots["supplier_name"], slots["supplier_cnpj"])
    return draft(
        "Nota Fiscal Eletrônica de Serviços",
        f"A nota fiscal nº {slots['invoice_number']} foi emitida em {view.calendar_date(slots['issue_date'])} "
        f"por {supplier}.",
        f"Discriminação dos serviços ou bens fornecidos: {unpunctuated(slots['description'])}.",
        f"Valor total da nota: {view.money(slots['amount'])}.",
    )


def invoice_tabular_lines(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "DANFE - Documento Auxiliar da Nota Fiscal",
        f"EMITENTE: {slots['supplier_name']} | {view.cnpj_tag(slots['supplier_cnpj'])}",
        f"NOTA FISCAL Nº {slots['invoice_number']} | DATA DE EMISSÃO {view.calendar_date(slots['issue_date'])}",
        f"DESCRIÇÃO DOS PRODUTOS E SERVIÇOS: {unpunctuated(slots['description'])}",
        f"VALOR TOTAL DA NOTA ........ {view.money(slots['amount'])}",
    )


def invoice_value_first(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    supplier = view.company(slots["supplier_name"], slots["supplier_cnpj"])
    return draft(
        "Fatura de Fornecimento",
        f"Valor cobrado: {view.money(slots['amount'])}, referente ao fornecimento a seguir: "
        f"{unpunctuated(slots['description'])}.",
        f"Nota fiscal nº {slots['invoice_number']}, datada de {view.calendar_date(slots['issue_date'])}, "
        f"emitida por {supplier}.",
    )


def attestation_formal_declaration(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    statement = attestation_statement(slots["statement_kind"], slots["exception_detail"], 0)
    return draft(
        "Atesto de Recebimento de Bens e Serviços",
        f"Atesto, para os devidos fins, que {statement}.",
        f"O atesto refere-se à(s) nota(s) fiscal(is) nº {view.joined(slots['invoice_numbers'])} e ao contrato "
        f"nº {slots['contract_number']}, cujo objeto é: {unpunctuated(slots['service_summary'])}.",
        f"{view.calendar_date(slots['issue_date'])}. {slots['attesting_name']}, {slots['attesting_role']}.",
    )


def attestation_narrative_receipt(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    statement = attestation_statement(slots["statement_kind"], slots["exception_detail"], 1)
    return draft(
        "Termo de Recebimento",
        f"Em {view.calendar_date(slots['issue_date'])}, eu, {slots['attesting_name']}, {slots['attesting_role']}, "
        f"conferi o objeto do contrato nº {slots['contract_number']} ({unpunctuated(slots['service_summary'])}), "
        f"faturado pela(s) NF {view.joined(slots['invoice_numbers'])}.",
        f"Conclusão do atesto: {statement}.",
    )


def attestation_tabular_record(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    statement = attestation_statement(slots["statement_kind"], slots["exception_detail"], 2)
    return draft(
        "Registro de Atesto",
        f"ATESTO | Fiscal: {slots['attesting_name']} ({slots['attesting_role']}) | "
        f"Data: {view.calendar_date(slots['issue_date'])}",
        f"Contrato: {slots['contract_number']} | Notas fiscais: {view.joined(slots['invoice_numbers'])}",
        f"Objeto: {unpunctuated(slots['service_summary'])}",
        f"Situação do recebimento: {statement}.",
    )


INVOICE_LAYOUTS: LayoutCatalog = {
    DocumentType.NOTA_FISCAL: (invoice_formal_prose, invoice_tabular_lines, invoice_value_first),
    DocumentType.ATESTO: (
        attestation_formal_declaration,
        attestation_narrative_receipt,
        attestation_tabular_record,
    ),
}
