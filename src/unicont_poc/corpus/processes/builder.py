from __future__ import annotations

from random import Random
from typing import Any

from unicont_poc.corpus.processes.accountability_process import build_accountability_process
from unicont_poc.corpus.processes.blueprint import ProcessBlueprint
from unicont_poc.corpus.catalog import checklist_for
from unicont_poc.corpus.processes.contracting_process import build_contracting_process
from unicont_poc.corpus.processes.identities import ORGANS, synthetic_process_number
from unicont_poc.corpus.processes.payment_process import build_payment_process
from unicont_poc.domain import DocumentType, ProcessCategory

MUTUALLY_EXCLUSIVE_IRREGULARITIES: tuple[frozenset[str], ...] = (
    frozenset({"PAG-01", "PAG-05", "PAG-07", "PAG-08", "PAG-09", "PAG-10"}),
    frozenset({"PAG-02", "PAG-11"}),
    frozenset({"PAG-03", "PAG-04"}),
    frozenset({"CON-03", "CON-08"}),
    frozenset({"CON-02", "CON-09"}),
    frozenset({"PRE-01", "PRE-06"}),
)


def _choose_irregularities(
    category: ProcessCategory, random_source: Random, irregularity_rate: float, can_duplicate_invoice: bool
) -> tuple[str, ...]:
    if random_source.random() >= irregularity_rate:
        return ()
    available = [item.code for item in checklist_for(category) if can_duplicate_invoice or item.code != "PAG-09"]
    random_source.shuffle(available)
    target_count = random_source.choices((1, 2, 3), weights=(70, 25, 5))[0]
    chosen: list[str] = []
    for code in available:
        conflicts = any(code in group and group & set(chosen) for group in MUTUALLY_EXCLUSIVE_IRREGULARITIES)
        if len(chosen) < target_count and not conflicts:
            chosen.append(code)
    return tuple(sorted(chosen))


def build_blueprint(
    index: int,
    category: ProcessCategory,
    template_family: str,
    random_source: Random,
    irregularity_rate: float,
    earlier_invoices: list[dict[str, Any]],
) -> ProcessBlueprint:
    blueprint = ProcessBlueprint(
        process_number=synthetic_process_number(random_source, index),
        category=category,
        organ=random_source.choice(ORGANS),
        template_family=template_family,
        irregularities=_choose_irregularities(category, random_source, irregularity_rate, bool(earlier_invoices)),
        complexity=random_source.choices(("baixa", "media", "alta"), weights=(45, 40, 15))[0],
    )
    if category is ProcessCategory.CONTRATACAO:
        build_contracting_process(blueprint, random_source)
    elif category is ProcessCategory.PRESTACAO_DE_CONTAS:
        build_accountability_process(blueprint, random_source)
    else:
        duplicates_invoice = "PAG-09" in blueprint.irregularities
        sibling_invoice = random_source.choice(earlier_invoices) if duplicates_invoice else None
        build_payment_process(blueprint, random_source, sibling_invoice)
        if not duplicates_invoice:
            earlier_invoices.extend(
                {key: plan.slots[key] for key in ("invoice_number", "supplier_cnpj", "amount")}
                for plan in blueprint.plans
                if plan.document_type is DocumentType.NOTA_FISCAL
            )
    return blueprint
