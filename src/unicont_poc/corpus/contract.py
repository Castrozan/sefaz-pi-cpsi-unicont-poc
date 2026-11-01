from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Any, Protocol

from unicont_poc.domain import DocumentType


@dataclass(frozen=True)
class DocumentPlan:
    document_id: str
    document_type: DocumentType
    slots: dict[str, Any]


@dataclass(frozen=True)
class DocumentDraft:
    title: str | None
    paragraphs: tuple[str, ...]


class TemplateFamily(Protocol):
    name: str

    def render(self, plan: DocumentPlan, random_source: Random) -> DocumentDraft: ...
