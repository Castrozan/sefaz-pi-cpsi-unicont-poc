from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from unicont_poc.analysis.process_view import ProcessView, SemanticVerdict
from unicont_poc.domain import DocumentType, ExtractedField


@dataclass
class ReviewAnswer:
    summary: str
    semantic_verdicts: dict[str, SemanticVerdict]
    type_corrections: dict[str, DocumentType] = field(default_factory=dict)
    field_fills: dict[str, dict[str, ExtractedField]] = field(default_factory=dict)
    model_identifier: str = "regras-sem-modelo"
    execution_mode: str = "deterministico"
    prompt_sha256: str = ""
    rejected_citations: int = 0


class ReviewStage(Protocol):
    def review(self, view: ProcessView) -> ReviewAnswer: ...
