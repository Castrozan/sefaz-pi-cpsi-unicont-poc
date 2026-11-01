from __future__ import annotations

from unicont_poc.corpus.contract import DocumentDraft
from unicont_poc.corpus.families.heldout.layout_support import LayoutCatalog, Slots, draft
from unicont_poc.corpus.families.heldout.presentation import ValueFormatter, unpunctuated
from unicont_poc.domain import DocumentType


def payments_listing_table(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    rows = [
        f"{view.calendar_date(expense['date'])} | {expense['supplier_name']} | "
        f"{unpunctuated(expense['description'])} | {view.money(expense['amount'])}"
        for expense in slots["expenses"]
    ]
    return draft(
        "Relação de Pagamentos Efetuados",
        f"Relação de pagamentos do convênio nº {slots['agreement_number']}, convenente {view.cnpj_tag(slots['partner_cnpj'])}, "
        f"emitida em {view.calendar_date(slots['issue_date'])}, para entrega em {view.calendar_date(slots['delivered_on'])}.",
        "DATA | FAVORECIDO | DESCRIÇÃO | VALOR",
        *rows,
        f"TOTAL DECLARADO DOS PAGAMENTOS ........ {view.money(slots['declared_total'])}",
    )


def payments_listing_narrative(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    entries = [
        f"{position}) Em {view.calendar_date(expense['date'])}, pagamento a {expense['supplier_name']}, "
        f"por {unpunctuated(expense['description'])}, no valor de {view.money(expense['amount'])}."
        for position, expense in enumerate(slots["expenses"], start=1)
    ]
    return draft(
        "Demonstrativo das Despesas Pagas",
        f"A convenente de {view.cnpj_tag(slots['partner_cnpj'])} declara os pagamentos a seguir, referentes ao "
        f"convênio nº {slots['agreement_number']}, em relação elaborada em {view.calendar_date(slots['issue_date'])}.",
        *entries,
        f"Soma declarada: {view.money(slots['declared_total'])}. Prestação de contas entregue em "
        f"{view.calendar_date(slots['delivered_on'])}.",
    )


def payments_listing_total_first(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    rows = [
        f"{unpunctuated(expense['description'])} - {expense['supplier_name']} - "
        f"{view.money(expense['amount'])} - pago em {view.calendar_date(expense['date'])}"
        for expense in slots["expenses"]
    ]
    return draft(
        "Despesas Realizadas com os Recursos",
        f"Total declarado: {view.money(slots['declared_total'])}, somados os pagamentos desta relação de pagamentos "
        f"do convênio {slots['agreement_number']} ({view.cnpj_tag(slots['partner_cnpj'])}).",
        *rows,
        f"Relação datada de {view.calendar_date(slots['issue_date'])}; entregue em "
        f"{view.calendar_date(slots['delivered_on'])}.",
    )


def bank_statement_summary(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Extrato da Conta Específica do Convênio",
        f"Extrato bancário da conta do convênio nº {slots['agreement_number']}, titular {slots['partner_name']}, "
        f"emitido em {view.calendar_date(slots['issue_date'])}.",
        f"Saldo inicial: {view.money(slots['opening_balance'])}. Saldo final: {view.money(slots['closing_balance'])}.",
        f"Saldo não utilizado do convênio: {view.money(slots['leftover'])}.",
    )


def bank_statement_tabular(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Extrato de Conta-Corrente",
        f"EXTRATO | TITULAR {slots['partner_name']} | CONVÊNIO Nº {slots['agreement_number']} | "
        f"{view.calendar_date(slots['issue_date'])}",
        f"SALDO ANTERIOR ........ {view.money(slots['opening_balance'])}",
        f"SALDO NÃO UTILIZADO ........ {view.money(slots['leftover'])}",
        f"SALDO ATUAL ........ {view.money(slots['closing_balance'])}",
    )


def bank_statement_narrative(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Posição da Conta Bancária",
        f"Na data de {view.calendar_date(slots['issue_date'])}, a conta bancária de {slots['partner_name']}, "
        f"vinculada ao convênio nº {slots['agreement_number']}, apresenta saldo de "
        f"{view.money(slots['closing_balance'])}.",
        f"A conta foi aberta com {view.money(slots['opening_balance'])}; o valor não utilizado do convênio é de "
        f"{view.money(slots['leftover'])}. Este é o extrato bancário correspondente.",
    )


def refund_receipt_formal(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Comprovante de Devolução de Saldo",
        f"Comprova-se a devolução, ao órgão concedente, de {view.money(slots['amount'])} do saldo do convênio "
        f"nº {slots['agreement_number']}.",
        f"Devolvente: {slots['partner_name']}. Data da devolução: {view.calendar_date(slots['issue_date'])}.",
    )


def refund_receipt_narrative(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Recibo de Restituição",
        f"Em {view.calendar_date(slots['issue_date'])}, {slots['partner_name']} devolveu o saldo remanescente do "
        f"convênio nº {slots['agreement_number']}, no valor de {view.money(slots['amount'])}.",
        "O presente documento serve como comprovante dessa devolução.",
    )


def refund_receipt_tabular(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Guia de Devolução",
        f"DEVOLUÇÃO DE SALDO | CONVÊNIO Nº {slots['agreement_number']}",
        f"DEPOSITANTE | {slots['partner_name']}",
        f"VALOR DEVOLVIDO | {view.money(slots['amount'])} | DATA {view.calendar_date(slots['issue_date'])}",
        "COMPROVANTE DE QUITAÇÃO DA DEVOLUÇÃO",
    )


SETTLEMENT_LAYOUTS: LayoutCatalog = {
    DocumentType.RELACAO_PAGAMENTOS: (payments_listing_table, payments_listing_narrative, payments_listing_total_first),
    DocumentType.EXTRATO_BANCARIO: (bank_statement_summary, bank_statement_tabular, bank_statement_narrative),
    DocumentType.COMPROVANTE_DEVOLUCAO: (refund_receipt_formal, refund_receipt_narrative, refund_receipt_tabular),
}
