from __future__ import annotations

from random import Random
from typing import Any

from unicont_poc.corpus.contract import DocumentDraft
from unicont_poc.corpus.formatting import brazilian_money, long_date, numeric_date
from unicont_poc.domain import DocumentType


def render_agreement(slots: dict[str, Any], random_source: Random) -> DocumentDraft:
    return DocumentDraft(
        f"TERMO DE CONVÊNIO Nº {slots['agreement_number']}",
        (
            f"CONCEDENTE: {slots['organ_name']}, CNPJ {slots['organ_cnpj']}.",
            f"CONVENENTE: {slots['partner_name']}, CNPJ {slots['partner_cnpj']}.",
            f"Processo nº {slots['process_number']}.",
            f"CLÁUSULA PRIMEIRA – DO OBJETO: {slots['object_text']}.",
            f"CLÁUSULA SEGUNDA – DO VALOR: {brazilian_money(slots['amount'])}.",
            f"CLÁUSULA TERCEIRA – DA VIGÊNCIA: de {numeric_date(slots['start_date'])} a {numeric_date(slots['end_date'])}.",
            f"CLÁUSULA QUARTA – DA PRESTAÇÃO DE CONTAS: a ser apresentada até {numeric_date(slots['report_deadline'])}.",
            f"Teresina, {long_date(slots['issue_date'])}. {slots['signer_name']}, Ordenador de Despesas.",
        ),
    )


def render_work_plan(slots: dict[str, Any], random_source: Random) -> DocumentDraft:
    return DocumentDraft(
        "PLANO DE TRABALHO",
        (
            f"Convênio nº {slots['agreement_number']}, Processo nº {slots['process_number']}.",
            f"Convenente: {slots['partner_name']}.",
            f"Objeto: {slots['object_text']}.",
            "Itens de despesa autorizados: " + "; ".join(slots["allowed_items"]) + ".",
            f"Valor total do plano: {brazilian_money(slots['amount'])}.",
        ),
    )


def render_execution_report(slots: dict[str, Any], random_source: Random) -> DocumentDraft:
    return DocumentDraft(
        "RELATÓRIO DE EXECUÇÃO DO OBJETO",
        (
            f"Convênio nº {slots['agreement_number']}, Processo nº {slots['process_number']}.",
            f"Convenente: {slots['partner_name']}, CNPJ {slots['partner_cnpj']}.",
            f"Relatamos a execução de {slots['object_text']}, com as metas pactuadas cumpridas.",
            f"Protocolado em {numeric_date(slots['delivered_on'])}.",
            f"{slots['signer_name']}, responsável pela entidade.",
        ),
    )


def render_payment_listing(slots: dict[str, Any], random_source: Random) -> DocumentDraft:
    expense_lines = tuple(
        f"{numeric_date(expense['date'])} | {expense['supplier_name']} | {expense['description']} | "
        f"{brazilian_money(expense['amount'])}"
        for expense in slots["expenses"]
    )
    return DocumentDraft(
        "RELAÇÃO DE PAGAMENTOS",
        (
            f"Convênio nº {slots['agreement_number']}, Processo nº {slots['process_number']}.",
            f"CNPJ da convenente: {slots['partner_cnpj']}.",
            *expense_lines,
            f"Total declarado: {brazilian_money(slots['declared_total'])}.",
        ),
    )


def render_bank_statement(slots: dict[str, Any], random_source: Random) -> DocumentDraft:
    return DocumentDraft(
        "EXTRATO BANCÁRIO DA CONTA ESPECÍFICA",
        (
            f"Convênio nº {slots['agreement_number']}, titular {slots['partner_name']}.",
            f"Processo nº {slots['process_number']}.",
            f"Saldo inicial: {brazilian_money(slots['opening_balance'])}.",
            f"Saldo final: {brazilian_money(slots['closing_balance'])}.",
            f"Emitido em {numeric_date(slots['issue_date'])}.",
        ),
    )


def render_refund_receipt(slots: dict[str, Any], random_source: Random) -> DocumentDraft:
    return DocumentDraft(
        "COMPROVANTE DE DEVOLUÇÃO DE SALDO",
        (
            f"Convênio nº {slots['agreement_number']}, Processo nº {slots['process_number']}.",
            f"Depositante: {slots['partner_name']}.",
            f"Valor devolvido ao Tesouro Estadual: {brazilian_money(slots['amount'])}.",
            f"Data: {numeric_date(slots['issue_date'])}.",
        ),
    )


ACCOUNTABILITY_RENDERERS = {
    DocumentType.TERMO_CONVENIO: render_agreement,
    DocumentType.PLANO_TRABALHO: render_work_plan,
    DocumentType.RELATORIO_EXECUCAO: render_execution_report,
    DocumentType.RELACAO_PAGAMENTOS: render_payment_listing,
    DocumentType.EXTRATO_BANCARIO: render_bank_statement,
    DocumentType.COMPROVANTE_DEVOLUCAO: render_refund_receipt,
}
