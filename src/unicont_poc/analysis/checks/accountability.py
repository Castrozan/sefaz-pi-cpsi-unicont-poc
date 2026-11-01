from __future__ import annotations

from decimal import Decimal

from unicont_poc.analysis.process_view import (
    ProcessView,
    document_evidence,
    prejudiced,
    presence_check,
    result,
    semantic_check,
    unverifiable,
)
from unicont_poc.corpus.catalog import CHECKLIST_BY_CODE
from unicont_poc.corpus.formatting import brazilian_money, numeric_date
from unicont_poc.domain import CheckResult, CheckStatus, DocumentType

TOLERANCE = Decimal("0.01")


def _balance_returned(view: ProcessView) -> CheckResult:
    item = CHECKLIST_BY_CODE["PRE-03"]
    statement = view.first(DocumentType.EXTRATO_BANCARIO)
    if statement is None:
        return prejudiced(item, "o extrato bancário")
    closing = statement.value("closing_balance")
    if closing is None:
        return unverifiable(item, "o saldo final do extrato", (document_evidence(statement),))
    receipt = view.first(DocumentType.COMPROVANTE_DEVOLUCAO)
    evidence = (statement.evidence_for("closing_balance"),)
    if receipt:
        return result(
            item, CheckStatus.CONFORME, "Comprovante de devolução localizado.", (*evidence, document_evidence(receipt))
        )
    if closing > 0:
        rationale = f"Saldo final de {brazilian_money(closing)} sem comprovante de devolução."
        return result(item, CheckStatus.NAO_CONFORME, rationale, evidence)
    return result(item, CheckStatus.CONFORME, "Conta encerrada com saldo zero; nada a devolver.", evidence)


def _expenses_add_up(view: ProcessView) -> CheckResult:
    item = CHECKLIST_BY_CODE["PRE-04"]
    listing = view.first(DocumentType.RELACAO_PAGAMENTOS)
    if listing is None or not listing.value("expenses") or listing.value("amount") is None:
        return unverifiable(item, "as despesas ou o total declarado")
    total = sum((row["amount"] for row in listing.value("expenses")), Decimal(0))
    declared = listing.value("amount")
    evidence = (listing.evidence_for("amount"),)
    if abs(total - declared) > TOLERANCE:
        rationale = f"Despesas somam {brazilian_money(total)}; declarado {brazilian_money(declared)}."
        return result(item, CheckStatus.NAO_CONFORME, rationale, evidence)
    return result(item, CheckStatus.CONFORME, f"Despesas somam {brazilian_money(total)}, igual ao declarado.", evidence)


def _expenses_within_term(view: ProcessView) -> CheckResult:
    item = CHECKLIST_BY_CODE["PRE-05"]
    listing, agreement = view.first(DocumentType.RELACAO_PAGAMENTOS), view.first(DocumentType.TERMO_CONVENIO)
    if listing is None or not listing.value("expenses"):
        return unverifiable(item, "as datas das despesas")
    if agreement is None or agreement.value("end_date") is None:
        return unverifiable(item, "a vigência do convênio")
    start, end = agreement.value("start_date"), agreement.value("end_date")
    for row in listing.value("expenses"):
        if not start <= row["date"] <= end:
            rationale = (
                f"Despesa de {numeric_date(row['date'])} fora da vigência, {numeric_date(start)} a {numeric_date(end)}."
            )
            evidence = (agreement.evidence_for("end_date"),)
            return result(item, CheckStatus.NAO_CONFORME, rationale, evidence)
    return result(
        item, CheckStatus.CONFORME, "Todas as despesas dentro da vigência.", (agreement.evidence_for("end_date"),)
    )


def _delivered_on_time(view: ProcessView) -> CheckResult:
    item = CHECKLIST_BY_CODE["PRE-06"]
    report, agreement = view.first(DocumentType.RELATORIO_EXECUCAO), view.first(DocumentType.TERMO_CONVENIO)
    if report is None:
        return prejudiced(item, "o relatório de execução")
    if agreement is None or agreement.value("report_deadline") is None or report.value("delivered_on") is None:
        return unverifiable(item, "o prazo ou a data de entrega")
    deadline, delivered = agreement.value("report_deadline"), report.value("delivered_on")
    evidence = (report.evidence_for("delivered_on"), agreement.evidence_for("report_deadline"))
    if delivered > deadline:
        rationale = f"Entregue em {numeric_date(delivered)}, após o prazo de {numeric_date(deadline)}."
        return result(item, CheckStatus.NAO_CONFORME, rationale, evidence)
    return result(item, CheckStatus.CONFORME, "Prestação de contas entregue no prazo.", evidence)


ACCOUNTABILITY_CHECKS = (
    lambda view: presence_check(
        view, CHECKLIST_BY_CODE["PRE-01"], DocumentType.RELATORIO_EXECUCAO, "Relatório de execução"
    ),
    lambda view: presence_check(view, CHECKLIST_BY_CODE["PRE-02"], DocumentType.EXTRATO_BANCARIO, "Extrato bancário"),
    _balance_returned,
    _expenses_add_up,
    _expenses_within_term,
    _delivered_on_time,
    lambda view: semantic_check(view, CHECKLIST_BY_CODE["PRE-07"]),
)
