from __future__ import annotations

from random import Random

from unicont_poc.corpus.contract import DocumentDraft, DocumentPlan
from unicont_poc.corpus.families.heldout.layout_support import LayoutCatalog
from unicont_poc.corpus.families.heldout.layouts.agreement_layouts import AGREEMENT_LAYOUTS
from unicont_poc.corpus.families.heldout.layouts.certificate_layouts import CERTIFICATE_LAYOUTS
from unicont_poc.corpus.families.heldout.layouts.commitment_layouts import COMMITMENT_LAYOUTS
from unicont_poc.corpus.families.heldout.layouts.contract_layouts import CONTRACT_LAYOUTS
from unicont_poc.corpus.families.heldout.layouts.designation_layouts import DESIGNATION_LAYOUTS
from unicont_poc.corpus.families.heldout.layouts.invoice_layouts import INVOICE_LAYOUTS
from unicont_poc.corpus.families.heldout.layouts.opinion_layouts import OPINION_LAYOUTS
from unicont_poc.corpus.families.heldout.layouts.planning_layouts import PLANNING_LAYOUTS
from unicont_poc.corpus.families.heldout.layouts.routine_layouts import ROUTINE_LAYOUTS
from unicont_poc.corpus.families.heldout.layouts.settlement_layouts import SETTLEMENT_LAYOUTS
from unicont_poc.corpus.families.heldout.presentation import ValueFormatter
from unicont_poc.corpus.families.heldout.process_frame import process_frame

TITLE_OMISSION_RATE = 0.25
FRAME_AT_START_RATE = 0.5

LAYOUTS_BY_TYPE: LayoutCatalog = {
    **INVOICE_LAYOUTS,
    **COMMITMENT_LAYOUTS,
    **CERTIFICATE_LAYOUTS,
    **PLANNING_LAYOUTS,
    **CONTRACT_LAYOUTS,
    **DESIGNATION_LAYOUTS,
    **OPINION_LAYOUTS,
    **AGREEMENT_LAYOUTS,
    **SETTLEMENT_LAYOUTS,
    **ROUTINE_LAYOUTS,
}


class HeldOutTemplateFamily:
    name = "inedita"

    def render(self, plan: DocumentPlan, random_source: Random) -> DocumentDraft:
        view = ValueFormatter.sample(random_source)
        layout = random_source.choice(LAYOUTS_BY_TYPE[plan.document_type])
        body = layout(plan.slots, view)
        frame = process_frame(plan.slots, view, random_source)
        frame_first = random_source.random() < FRAME_AT_START_RATE
        paragraphs = (frame, *body.paragraphs) if frame_first else (*body.paragraphs, frame)
        title = None if random_source.random() < TITLE_OMISSION_RATE else body.title
        return DocumentDraft(title, paragraphs)
