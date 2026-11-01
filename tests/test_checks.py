from support import classified, regular_payment_documents, view_with

from unicont_poc.analysis.checks import run_checks
from unicont_poc.domain import CheckStatus, DocumentType, ProcessCategory


def statuses(documents):
    return {check.code: check for check in run_checks(view_with(ProcessCategory.PAGAMENTO, documents))}


def test_regular_payment_has_no_failed_rule():
    results = statuses(regular_payment_documents())
    failed = [code for code, check in results.items() if check.status is CheckStatus.NAO_CONFORME]
    assert failed == []


def test_paid_above_invoices_and_commitment_is_flagged_with_evidence():
    results = statuses(regular_payment_documents(paid="3.000,00"))
    assert results["PAG-05"].status is CheckStatus.NAO_CONFORME
    assert results["PAG-06"].status is CheckStatus.NAO_CONFORME
    assert any("3.000,00" in entry.quote for entry in results["PAG-05"].evidence)


def test_missing_invoice_is_failure_and_dependents_are_prejudiced_not_false_alarms():
    documents = [d for d in regular_payment_documents() if d.document_type is not DocumentType.NOTA_FISCAL]
    results = statuses(documents)
    assert results["PAG-01"].status is CheckStatus.NAO_CONFORME
    assert results["PAG-05"].status is CheckStatus.PREJUDICADO


def test_renewed_certificate_clears_the_expired_one():
    expired = classified(DocumentType.CERTIDAO_FGTS, "Válida até 01/01/2026.", "d-009")
    results = statuses([*regular_payment_documents(), expired])
    assert results["PAG-04"].status is CheckStatus.CONFORME


def test_expired_certificate_alone_is_flagged():
    documents = [d for d in regular_payment_documents() if d.document_type is not DocumentType.CERTIDAO_FGTS]
    documents.append(classified(DocumentType.CERTIDAO_FGTS, "Válida até 01/01/2026.", "d-009"))
    assert statuses(documents)["PAG-04"].status is CheckStatus.NAO_CONFORME


def test_unreadable_amount_routes_to_human_instead_of_guessing():
    documents = regular_payment_documents()
    documents[1] = classified(DocumentType.NOTA_FISCAL, "Nota fiscal ilegível", "d-002")
    assert statuses(documents)["PAG-05"].status is CheckStatus.NAO_VERIFICAVEL


def test_semantic_criteria_stay_unverified_without_a_reader():
    assert statuses(regular_payment_documents())["PAG-10"].status is CheckStatus.NAO_VERIFICAVEL
