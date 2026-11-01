from __future__ import annotations

from typing import Any, Callable

from unicont_poc.corpus.contract import DocumentDraft
from unicont_poc.corpus.families.heldout.presentation import ValueFormatter
from unicont_poc.domain import DocumentType

Slots = dict[str, Any]
Layout = Callable[[Slots, ValueFormatter], DocumentDraft]
LayoutCatalog = dict[DocumentType, tuple[Layout, ...]]


def draft(title: str, *paragraphs: str) -> DocumentDraft:
    return DocumentDraft(title, tuple(paragraphs))
