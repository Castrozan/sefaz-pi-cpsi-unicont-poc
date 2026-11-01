from __future__ import annotations

from decimal import Decimal

from unicont_poc.analysis.parsing import find_cnpjs
from unicont_poc.analysis.process_view import (
    ProcessView,
    document_evidence,
    presence_check,
    result,
    semantic_check,
    unverifiable,
)
from unicont_poc.corpus.catalog import CHECKLIST_BY_CODE
from unicont_poc.corpus.formatting import brazilian_money
from unicont_poc.domain import CheckResult, CheckStatus, DocumentType

MINIMUM_QUOTED_SUPPLIERS = 3
ESTIMATE_SOURCES = (
    DocumentType.PESQUISA_PRECOS,
    DocumentType.TERMO_REFERENCIA,
    DocumentType.ESTUDO_TECNICO_PRELIMINAR,
)


def _quoted_suppliers(view: ProcessView) -> CheckResult:
    item = CHECKLIST_BY_CODE["CON-04"]
    survey = view.first(DocumentType.PESQUISA_PRECOS)
    if survey is None:
        return result(item, CheckStatus.NAO_CONFORME, "Pesquisa de preços não localizada.")
    filled_count = survey.value("quote_count")
    count = (
        filled_count
        if filled_count is not None
        else len({match.value for match in find_cnpjs(survey.document.canonical_text)})
    )
    evidence = (document_evidence(survey),)
    if count >= MINIMUM_QUOTED_SUPPLIERS:
        return result(item, CheckStatus.CONFORME, f"{count} fornecedores consultados.", evidence)
    if survey.document.was_scanned and filled_count is None:
        return unverifiable(item, "a quantidade de fornecedores no documento digitalizado", evidence)
    return result(item, CheckStatus.NAO_CONFORME, f"Apenas {count} fornecedor(es) consultado(s).", evidence)


def _within_estimate(view: ProcessView) -> CheckResult:
    item = CHECKLIST_BY_CODE["CON-05"]
    contract = view.first(DocumentType.CONTRATO)
    sources = [document for document in view.of_type(*ESTIMATE_SOURCES) if document.value("amount") is not None]
    if contract is None or contract.value("amount") is None or not sources:
        return unverifiable(item, "o valor contratado ou o valor estimado")
    estimate: Decimal = sources[0].value("amount")
    contracted: Decimal = contract.value("amount")
    evidence = (contract.evidence_for("amount"), sources[0].evidence_for("amount"))
    if contracted > estimate:
        rationale = f"Contratado {brazilian_money(contracted)} acima do estimado, {brazilian_money(estimate)}."
        return result(item, CheckStatus.NAO_CONFORME, rationale, evidence)
    return result(item, CheckStatus.CONFORME, f"Contratado {brazilian_money(contracted)} dentro do estimado.", evidence)


def _inspector_designated(view: ProcessView) -> CheckResult:
    item = CHECKLIST_BY_CODE["CON-06"]
    ordinance = view.first(DocumentType.PORTARIA_FISCAL)
    if ordinance:
        return result(item, CheckStatus.CONFORME, "Portaria de designação localizada.", (document_evidence(ordinance),))
    contract = view.first(DocumentType.CONTRATO)
    if contract and contract.value("fiscal_name"):
        rationale = f"Fiscal indicado no contrato: {contract.value('fiscal_name')}."
        return result(item, CheckStatus.CONFORME, rationale, (contract.evidence_for("fiscal_name"),))
    return result(item, CheckStatus.NAO_CONFORME, "Sem portaria de designação e sem fiscal nominado no contrato.")


def _proposal_matches_contract(view: ProcessView) -> CheckResult:
    item = CHECKLIST_BY_CODE["CON-07"]
    proposal, contract = view.first(DocumentType.PROPOSTA), view.first(DocumentType.CONTRATO)
    if not proposal or not contract or not proposal.value("cnpj") or not contract.value("cnpj"):
        return unverifiable(item, "o CNPJ da proposta ou do contrato")
    evidence = (proposal.evidence_for("cnpj"), contract.evidence_for("cnpj"))
    if proposal.value("cnpj") != contract.value("cnpj"):
        rationale = f"Proposta de {proposal.value('cnpj')}; contrato com {contract.value('cnpj')}."
        return result(item, CheckStatus.NAO_CONFORME, rationale, evidence)
    return result(item, CheckStatus.CONFORME, "CNPJ da proposta igual ao do contrato.", evidence)


CONTRACTING_CHECKS = (
    lambda view: presence_check(view, CHECKLIST_BY_CODE["CON-01"], DocumentType.ESTUDO_TECNICO_PRELIMINAR, "ETP"),
    lambda view: presence_check(
        view, CHECKLIST_BY_CODE["CON-02"], DocumentType.TERMO_REFERENCIA, "Termo de referência"
    ),
    lambda view: presence_check(view, CHECKLIST_BY_CODE["CON-03"], DocumentType.PARECER_JURIDICO, "Parecer jurídico"),
    _quoted_suppliers,
    _within_estimate,
    _inspector_designated,
    _proposal_matches_contract,
    lambda view: semantic_check(view, CHECKLIST_BY_CODE["CON-08"]),
    lambda view: semantic_check(view, CHECKLIST_BY_CODE["CON-09"]),
)
