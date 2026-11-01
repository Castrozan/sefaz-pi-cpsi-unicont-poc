from __future__ import annotations

from dataclasses import asdict
from datetime import date
from decimal import Decimal

from unicont_poc.domain import CheckResult, ClassifiedDocument


def _plain(value: object) -> object:
    if isinstance(value, (Decimal, date)):
        return str(value)
    if isinstance(value, list):
        return [_plain(entry) for entry in value]
    if isinstance(value, dict):
        return {key: _plain(entry) for key, entry in value.items()}
    return value


def serialize_document(classified: ClassifiedDocument) -> dict:
    document = classified.document
    return {
        "document_id": document.document_id,
        "declared_title": document.declared_title,
        "document_type": classified.document_type.value,
        "label": classified.label,
        "confidence": classified.confidence,
        "method": classified.method,
        "sha256": document.sha256,
        "was_scanned": document.was_scanned,
        "page_count": len(document.pages),
        "fields": {
            name: {
                "value": _plain(extracted.value),
                "page": extracted.evidence.page_number,
                "quote": extracted.evidence.quote,
                "method": extracted.method,
            }
            for name, extracted in classified.fields.items()
        },
    }


def serialize_check(check: CheckResult) -> dict:
    return {**asdict(check), "status": check.status.value, "evidence": [asdict(entry) for entry in check.evidence]}
