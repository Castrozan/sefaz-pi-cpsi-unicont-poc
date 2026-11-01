from __future__ import annotations

from random import Random

from unicont_poc.corpus.contract import DocumentDraft, DocumentPlan
from unicont_poc.corpus.families.standard.accountability import ACCOUNTABILITY_RENDERERS
from unicont_poc.corpus.families.standard.contracting import CONTRACTING_RENDERERS
from unicont_poc.corpus.families.standard.payment import PAYMENT_RENDERERS
from unicont_poc.corpus.families.standard.routine import ROUTINE_RENDERERS


class StandardTemplateFamily:
    name = "padrao"

    def __init__(self) -> None:
        self.renderers = {
            **PAYMENT_RENDERERS,
            **CONTRACTING_RENDERERS,
            **ACCOUNTABILITY_RENDERERS,
            **ROUTINE_RENDERERS,
        }

    def render(self, plan: DocumentPlan, random_source: Random) -> DocumentDraft:
        return self.renderers[plan.document_type](plan.slots, random_source)
