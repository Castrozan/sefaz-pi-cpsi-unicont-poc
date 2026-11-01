from __future__ import annotations

from dataclasses import dataclass, field

from unicont_poc.corpus.catalog import ChecklistItem
from unicont_poc.domain import (
    AdministrativeProcess,
    CheckResult,
    CheckStatus,
    ClassifiedDocument,
    DocumentType,
    Evidence,
)


@dataclass(frozen=True)
class SemanticVerdict:
    status: CheckStatus
    rationale: str
    evidence: tuple[Evidence, ...]
    method: str


@dataclass
class ProcessView:
    process: AdministrativeProcess
    documents: list[ClassifiedDocument]
    semantic_verdicts: dict[str, SemanticVerdict] = field(default_factory=dict)
    duplicate_of: dict[str, str] = field(default_factory=dict)

    def of_type(self, *document_types: DocumentType) -> list[ClassifiedDocument]:
        return [document for document in self.documents if document.document_type in document_types]

    def first(self, document_type: DocumentType) -> ClassifiedDocument | None:
        matches = self.of_type(document_type)
        return matches[0] if matches else None


def document_evidence(document: ClassifiedDocument) -> Evidence:
    text = document.document.canonical_text
    return Evidence(document.document.document_id, 1, text[:140], document.label)


def result(
    item: ChecklistItem,
    status: CheckStatus,
    rationale: str,
    evidence: tuple[Evidence | None, ...] = (),
    method: str = "regra",
) -> CheckResult:
    return CheckResult(
        item.code,
        item.title,
        item.legal_basis,
        status,
        rationale,
        method,
        tuple(entry for entry in evidence if entry is not None),
    )


def presence_check(view: ProcessView, item: ChecklistItem, document_type: DocumentType, label: str) -> CheckResult:
    found = view.of_type(document_type)
    if not found:
        return result(item, CheckStatus.NAO_CONFORME, f"{label} não localizado(a) entre os documentos do processo.")
    return result(item, CheckStatus.CONFORME, f"{label} localizado(a).", (document_evidence(found[0]),))


def prejudiced(item: ChecklistItem, missing: str) -> CheckResult:
    return result(item, CheckStatus.PREJUDICADO, f"Verificação prejudicada: falta {missing}.")


def unverifiable(item: ChecklistItem, missing: str, evidence: tuple[Evidence | None, ...] = ()) -> CheckResult:
    return result(
        item, CheckStatus.NAO_VERIFICAVEL, f"Não foi possível ler {missing}; requer conferência humana.", evidence
    )


def semantic_check(view: ProcessView, item: ChecklistItem) -> CheckResult:
    verdict = view.semantic_verdicts.get(item.code)
    if verdict is None:
        return result(item, CheckStatus.NAO_VERIFICAVEL, "Sem leitura semântica disponível para este critério.")
    return result(item, verdict.status, verdict.rationale, verdict.evidence, verdict.method)
