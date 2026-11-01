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

CERTIFICATE_LABELS = {
    DocumentType.CERTIDAO_FEDERAL: "certidão federal",
    DocumentType.CERTIDAO_FGTS: "certificado do FGTS",
    DocumentType.CERTIDAO_TRABALHISTA: "certidão trabalhista",
}
TOLERANCE = Decimal("0.01")


def _invoices_present(view: ProcessView) -> CheckResult:
    return presence_check(view, CHECKLIST_BY_CODE["PAG-01"], DocumentType.NOTA_FISCAL, "Nota fiscal")


def _attestation_present(view: ProcessView) -> CheckResult:
    return presence_check(view, CHECKLIST_BY_CODE["PAG-02"], DocumentType.ATESTO, "Atesto de recebimento")


def _certificates_present(view: ProcessView) -> CheckResult:
    item = CHECKLIST_BY_CODE["PAG-03"]
    missing = [label for kind, label in CERTIFICATE_LABELS.items() if not view.of_type(kind)]
    if missing:
        return result(item, CheckStatus.NAO_CONFORME, f"Não localizado(s): {', '.join(missing)}.")
    certificates = view.of_type(*CERTIFICATE_LABELS)
    return result(
        item, CheckStatus.CONFORME, "As três certidões foram localizadas.", tuple(map(document_evidence, certificates))
    )


def _certificates_valid(view: ProcessView) -> CheckResult:
    item = CHECKLIST_BY_CODE["PAG-04"]
    order = view.first(DocumentType.ORDEM_PAGAMENTO)
    payment_date = order.value("payment_date") if order else None
    if payment_date is None:
        return unverifiable(item, "a data de pagamento")
    evidence = [order.evidence_for("payment_date")]
    for kind, label in CERTIFICATE_LABELS.items():
        certificates = view.of_type(kind)
        if not certificates:
            continue
        expirations = [(document.value("valid_until"), document) for document in certificates]
        readable = [entry for entry in expirations if entry[0] is not None]
        if not readable:
            return unverifiable(item, f"a validade da {label}", (document_evidence(certificates[0]),))
        latest, latest_document = max(readable, key=lambda entry: entry[0])
        if latest < payment_date:
            return result(
                item,
                CheckStatus.NAO_CONFORME,
                f"{label.capitalize()} venceu em {numeric_date(latest)}, antes do pagamento em {numeric_date(payment_date)}.",
                (latest_document.evidence_for("valid_until"), *evidence),
            )
        evidence.append(latest_document.evidence_for("valid_until"))
    return result(item, CheckStatus.CONFORME, f"Certidões válidas em {numeric_date(payment_date)}.", tuple(evidence))


def _paid_matches_invoices(view: ProcessView) -> CheckResult:
    item = CHECKLIST_BY_CODE["PAG-05"]
    invoices = view.of_type(DocumentType.NOTA_FISCAL)
    order = view.first(DocumentType.ORDEM_PAGAMENTO)
    if not invoices:
        return prejudiced(item, "a nota fiscal")
    if order is None or order.value("amount") is None:
        return unverifiable(item, "o valor pago")
    amounts = [invoice.value("amount") for invoice in invoices]
    if None in amounts:
        return unverifiable(item, "o valor da nota fiscal", (document_evidence(invoices[0]),))
    total, paid = sum(amounts, Decimal(0)), order.value("amount")
    evidence = (*(invoice.evidence_for("amount") for invoice in invoices), order.evidence_for("amount"))
    if abs(total - paid) > TOLERANCE:
        rationale = f"Pago {brazilian_money(paid)}, mas as notas somam {brazilian_money(total)}."
        return result(item, CheckStatus.NAO_CONFORME, rationale, evidence)
    return result(item, CheckStatus.CONFORME, f"Pago {brazilian_money(paid)}, igual à soma das notas.", evidence)


def _paid_within_commitment(view: ProcessView) -> CheckResult:
    item = CHECKLIST_BY_CODE["PAG-06"]
    commitments = view.of_type(DocumentType.NOTA_EMPENHO)
    order = view.first(DocumentType.ORDEM_PAGAMENTO)
    amounts = [commitment.value("amount") for commitment in commitments]
    if not commitments or None in amounts or order is None or order.value("amount") is None:
        return unverifiable(item, "os valores de empenho e de pagamento")
    committed, paid = sum(amounts, Decimal(0)), order.value("amount")
    evidence = (*(commitment.evidence_for("amount") for commitment in commitments), order.evidence_for("amount"))
    if paid > committed + TOLERANCE:
        rationale = f"Pago {brazilian_money(paid)} acima do empenhado, {brazilian_money(committed)}."
        return result(item, CheckStatus.NAO_CONFORME, rationale, evidence)
    return result(item, CheckStatus.CONFORME, f"Empenhado {brazilian_money(committed)} cobre o pagamento.", evidence)


def _supplier_matches_contract(view: ProcessView) -> CheckResult:
    item = CHECKLIST_BY_CODE["PAG-07"]
    invoices = view.of_type(DocumentType.NOTA_FISCAL)
    contract = view.first(DocumentType.CONTRATO)
    if not invoices:
        return prejudiced(item, "a nota fiscal")
    if contract is None or contract.value("cnpj") is None:
        return unverifiable(item, "o CNPJ do contrato")
    for invoice in invoices:
        if invoice.value("cnpj") is None:
            return unverifiable(item, "o CNPJ da nota fiscal", (document_evidence(invoice),))
        if invoice.value("cnpj") != contract.value("cnpj"):
            rationale = f"Nota emitida por {invoice.value('cnpj')}; contrato com {contract.value('cnpj')}."
            evidence = (invoice.evidence_for("cnpj"), contract.evidence_for("cnpj"))
            return result(item, CheckStatus.NAO_CONFORME, rationale, evidence)
    evidence = (invoices[0].evidence_for("cnpj"), contract.evidence_for("cnpj"))
    return result(item, CheckStatus.CONFORME, "CNPJ da nota igual ao do contrato.", evidence)


def _commitment_before_expense(view: ProcessView) -> CheckResult:
    item = CHECKLIST_BY_CODE["PAG-08"]
    invoices = view.of_type(DocumentType.NOTA_FISCAL)
    commitments = view.of_type(DocumentType.NOTA_EMPENHO)
    if not invoices:
        return prejudiced(item, "a nota fiscal")
    invoice_dates = [(document.value("issue_date"), document) for document in invoices if document.value("issue_date")]
    commitment_dates = [
        (document.value("issue_date"), document) for document in commitments if document.value("issue_date")
    ]
    if not invoice_dates or not commitment_dates:
        return unverifiable(item, "as datas de empenho e de nota fiscal")
    first_invoice, invoice = min(invoice_dates, key=lambda entry: entry[0])
    first_commitment, commitment = min(commitment_dates, key=lambda entry: entry[0])
    evidence = (commitment.evidence_for("issue_date"), invoice.evidence_for("issue_date"))
    if first_commitment > first_invoice:
        rationale = f"Empenho de {numeric_date(first_commitment)} posterior à nota de {numeric_date(first_invoice)}."
        return result(item, CheckStatus.NAO_CONFORME, rationale, evidence)
    return result(item, CheckStatus.CONFORME, "Empenho anterior à nota fiscal.", evidence)


def _invoice_not_duplicated(view: ProcessView) -> CheckResult:
    item = CHECKLIST_BY_CODE["PAG-09"]
    invoices = view.of_type(DocumentType.NOTA_FISCAL)
    if not invoices:
        return prejudiced(item, "a nota fiscal")
    for invoice in invoices:
        other_process = view.duplicate_of.get(invoice.document.document_id)
        if other_process:
            rationale = f"Nota {invoice.value('invoice_number')} já consta do processo {other_process}."
            return result(item, CheckStatus.NAO_CONFORME, rationale, (invoice.evidence_for("invoice_number"),))
    if any(invoice.value("invoice_number") is None for invoice in invoices):
        return unverifiable(item, "o número da nota fiscal", (document_evidence(invoices[0]),))
    return result(item, CheckStatus.CONFORME, "Sem repetição da nota no ciclo analisado.")


PAYMENT_CHECKS = (
    _invoices_present,
    _attestation_present,
    _certificates_present,
    _certificates_valid,
    _paid_matches_invoices,
    _paid_within_commitment,
    _supplier_matches_contract,
    _commitment_before_expense,
    _invoice_not_duplicated,
    lambda view: semantic_check(view, CHECKLIST_BY_CODE["PAG-10"]),
    lambda view: semantic_check(view, CHECKLIST_BY_CODE["PAG-11"]),
)
