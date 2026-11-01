from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal

from unicont_poc.analysis.checks import run_checks
from unicont_poc.analysis.classifier import classify_document
from unicont_poc.analysis.extractors import extract_fields
from unicont_poc.analysis.opinion import draft_opinion, overall_verdict
from unicont_poc.analysis.process_view import ProcessView
from unicont_poc.analysis.review.review_contract import ReviewAnswer, ReviewStage
from unicont_poc.analysis.risk import assess_risk
from unicont_poc.analysis.serialization import serialize_check, serialize_document
from unicont_poc.corpus.catalog import CHECKLIST
from unicont_poc.domain import AdministrativeProcess, DocumentType

PIPELINE_VERSION = "0.1.0"
CRITERIA_VERSION = "checklist-ilustrativo-2026-10"
VALUE_SOURCES = (DocumentType.ORDEM_PAGAMENTO, DocumentType.CONTRATO, DocumentType.TERMO_CONVENIO)


@dataclass
class PreparedProcess:
    view: ProcessView
    answer: ReviewAnswer
    timings: dict[str, float] = field(default_factory=dict)


def classify_process(process: AdministrativeProcess) -> ProcessView:
    documents = [classify_document(document) for document in process.documents]
    for document in documents:
        extract_fields(document)
    return ProcessView(process, documents)


def _apply_review(view: ProcessView, answer: ReviewAnswer) -> None:
    view.semantic_verdicts = answer.semantic_verdicts
    for document in view.documents:
        document_id = document.document.document_id
        corrected_type = answer.type_corrections.get(document_id)
        if corrected_type and corrected_type is not document.document_type:
            document.document_type = corrected_type
            document.method = "modelo"
            extract_fields(document)
        document.fields.update(answer.field_fills.get(document_id, {}))


def prepare_process(view: ProcessView, review: ReviewStage) -> PreparedProcess:
    started = time.perf_counter()
    answer = review.review(view)
    _apply_review(view, answer)
    return PreparedProcess(view, answer, {"revisao_segundos": time.perf_counter() - started})


def _process_value(view: ProcessView) -> Decimal | None:
    for document_type in VALUE_SOURCES:
        document = view.first(document_type)
        if document and document.value("amount") is not None:
            return document.value("amount")
    return None


def conclude_process(prepared: PreparedProcess) -> dict:
    view, answer = prepared.view, prepared.answer
    started = time.perf_counter()
    checks = run_checks(view)
    value = _process_value(view)
    risk = assess_risk(checks, value)
    opinion = draft_opinion(view.process.process_number, view.process.organ_name, answer.summary, checks)
    timings = {**prepared.timings, "verificacao_segundos": time.perf_counter() - started}
    return {
        "analysis_id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "process_number": view.process.process_number,
        "category": view.process.category.value,
        "organ_name": view.process.organ_name,
        "nucleus_code": view.process.nucleus_code,
        "process_value": str(value) if value is not None else None,
        "documents": [serialize_document(document) for document in view.documents],
        "checks": [serialize_check(check) for check in checks],
        "verdict": overall_verdict(checks),
        "risk": {"level": risk.level.value, "priority_score": risk.priority_score, "reasons": list(risk.reasons)},
        "summary": answer.summary,
        "opinion_draft": opinion,
        "criteria": {
            "version": CRITERIA_VERSION,
            "applied": [item.code for item in CHECKLIST if item.category is view.process.category],
        },
        "model": {
            "identifier": answer.model_identifier,
            "execution_mode": answer.execution_mode,
            "prompt_sha256": answer.prompt_sha256,
            "rejected_citations": answer.rejected_citations,
            "pipeline_version": PIPELINE_VERSION,
        },
        "timings": timings,
    }
