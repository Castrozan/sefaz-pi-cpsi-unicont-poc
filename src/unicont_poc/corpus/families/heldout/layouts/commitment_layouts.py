from __future__ import annotations

from unicont_poc.corpus.contract import DocumentDraft
from unicont_poc.corpus.families.heldout.layout_support import LayoutCatalog, Slots, draft
from unicont_poc.corpus.families.heldout.presentation import ValueFormatter, unpunctuated
from unicont_poc.domain import DocumentType

COMMITMENT_KIND_LABELS = {
    "original": "empenho ordinário",
    "reforco": "reforço de empenho, acréscimo a empenho anterior da mesma despesa",
}


def commitment_formal_note(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    supplier = view.company(slots["supplier_name"], slots["supplier_cnpj"])
    return draft(
        "Nota de Empenho",
        f"Nota de empenho nº {slots['commitment_number']}, emitida em {view.calendar_date(slots['issue_date'])}, "
        f"do tipo {COMMITMENT_KIND_LABELS[slots['kind']]}, em favor de {supplier}.",
        f"Valor empenhado: {view.money(slots['amount'])}. "
        f"Rubrica orçamentária (natureza da despesa): {slots['budget_line']}.",
        f"Finalidade da despesa: {unpunctuated(slots['description'])}.",
    )


def commitment_tabular_ledger(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "NE - Registro de Empenho da Despesa",
        f"NOTA DE EMPENHO Nº {slots['commitment_number']} | EMISSÃO {view.calendar_date(slots['issue_date'])}",
        f"TIPO: {COMMITMENT_KIND_LABELS[slots['kind']].upper()}",
        f"CREDOR: {slots['supplier_name']} | {view.cnpj_tag(slots['supplier_cnpj'])}",
        f"ELEMENTO DE DESPESA {slots['budget_line']} ........ {view.money(slots['amount'])}",
        f"HISTÓRICO: {unpunctuated(slots['description'])}",
    )


def commitment_declaratory_prose(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Empenho da Despesa",
        f"Fica empenhado, na data de {view.calendar_date(slots['issue_date'])}, o montante de "
        f"{view.money(slots['amount'])}, à conta da rubrica {slots['budget_line']}, em favor de "
        f"{view.company(slots['supplier_name'], slots['supplier_cnpj'])}.",
        f"Trata-se da nota de empenho nº {slots['commitment_number']}, classificada como "
        f"{COMMITMENT_KIND_LABELS[slots['kind']]}, destinada a: {unpunctuated(slots['description'])}.",
    )


def settlement_formal_record(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    supplier = view.company(slots["supplier_name"], slots["supplier_cnpj"])
    return draft(
        "Liquidação da Despesa",
        f"Liquidada em {view.calendar_date(slots['issue_date'])}, sob o nº {slots['settlement_number']}, a despesa "
        f"do empenho nº {slots['commitment_number']}.",
        f"Credor: {supplier}. Documentos fiscais liquidados: nota(s) fiscal(is) nº "
        f"{view.joined(slots['invoice_numbers'])}.",
        f"Valor liquidado: {view.money(slots['amount'])}.",
    )


def settlement_tabular_entry(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "NL - Nota de Liquidação",
        f"LIQUIDAÇÃO Nº {slots['settlement_number']} | DATA {view.calendar_date(slots['issue_date'])}",
        f"EMPENHO DE ORIGEM: {slots['commitment_number']} | NF: {view.joined(slots['invoice_numbers'])}",
        f"CREDOR: {slots['supplier_name']} | {view.cnpj_tag(slots['supplier_cnpj'])}",
        f"VALOR LIQUIDADO ........ {view.money(slots['amount'])}",
    )


def settlement_creditor_first(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Reconhecimento da Dívida - Liquidação",
        f"Reconhece-se como devido ao credor {slots['supplier_name']} ({view.cnpj_tag(slots['supplier_cnpj'])}) "
        f"o valor de {view.money(slots['amount'])}, em liquidação datada de "
        f"{view.calendar_date(slots['issue_date'])}.",
        f"A liquidação nº {slots['settlement_number']} vincula-se ao empenho {slots['commitment_number']} e às "
        f"notas fiscais {view.joined(slots['invoice_numbers'])}.",
    )


def payment_order_formal(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Ordem de Pagamento",
        f"A ordem de pagamento nº {slots['payment_order_number']}, emitida em "
        f"{view.calendar_date(slots['issue_date'])}, determina o pagamento de {view.money(slots['amount'])} ao "
        f"favorecido {view.company(slots['supplier_name'], slots['supplier_cnpj'])}.",
        f"O crédito será efetuado na conta bancária nº {slots['bank_account']}.",
    )


def payment_order_tabular(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "OB - Ordem Bancária",
        f"ORDEM Nº {slots['payment_order_number']} | EMITIDA EM {view.calendar_date(slots['issue_date'])}",
        f"FAVORECIDO: {slots['supplier_name']} | {view.cnpj_tag(slots['supplier_cnpj'])}",
        f"CONTA DE DESTINO: {slots['bank_account']}",
        f"VALOR A PAGAR ........ {view.money(slots['amount'])}",
    )


def payment_order_authorization(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Autorização de Pagamento",
        f"Autoriza-se o pagamento de {view.money(slots['amount'])} a {slots['supplier_name']} "
        f"({view.cnpj_tag(slots['supplier_cnpj'])}), por meio de crédito na conta {slots['bank_account']}.",
        f"Esta é a ordem de pagamento nº {slots['payment_order_number']}, de {view.calendar_date(slots['issue_date'])}.",
    )


COMMITMENT_LAYOUTS: LayoutCatalog = {
    DocumentType.NOTA_EMPENHO: (commitment_formal_note, commitment_tabular_ledger, commitment_declaratory_prose),
    DocumentType.LIQUIDACAO: (settlement_formal_record, settlement_tabular_entry, settlement_creditor_first),
    DocumentType.ORDEM_PAGAMENTO: (payment_order_formal, payment_order_tabular, payment_order_authorization),
}
