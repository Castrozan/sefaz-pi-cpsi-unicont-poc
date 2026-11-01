from __future__ import annotations

import hashlib
import json
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from random import Random
from typing import Any

from unicont_poc.corpus.blueprint import ProcessBlueprint
from unicont_poc.corpus.builder import build_blueprint
from unicont_poc.corpus.contract import DocumentPlan, TemplateFamily
from unicont_poc.corpus.family_standard import StandardTemplateFamily
from unicont_poc.corpus.rendering import convert_to_scanned_pdf, render_text_pdf
from unicont_poc.domain import ProcessCategory

GENERIC_TITLES = ("Documento externo", "Anexo", "Documento", "Digitalização")
GENERIC_TITLE_RATE = 0.4
SCAN_RATE = 0.12
AMOUNT_SLOTS = ("amount", "declared_total", "estimated_amount")
CNPJ_SLOTS = ("supplier_cnpj", "partner_cnpj")


@dataclass(frozen=True)
class CorpusRequest:
    name: str
    seed: int
    counts: dict[ProcessCategory, int]
    template_families: tuple[str, ...]
    irregularity_rate: float = 0.45


def template_family_named(name: str) -> TemplateFamily:
    if name == "padrao":
        return StandardTemplateFamily()
    from unicont_poc.corpus.family_heldout import HeldOutTemplateFamily

    return HeldOutTemplateFamily()


def expected_fields(plan: DocumentPlan) -> dict[str, str]:
    fields = {"process_number": plan.slots["process_number"]}
    for slot in AMOUNT_SLOTS:
        if plan.slots.get(slot) is not None:
            fields["amount"] = f"{plan.slots[slot]:.2f}"
            break
    for slot in CNPJ_SLOTS:
        if plan.slots.get(slot):
            fields["cnpj"] = plan.slots[slot]
            break
    return fields


def _render_process(arguments: tuple[ProcessBlueprint, int, Path]) -> dict[str, Any]:
    blueprint, process_seed, output_directory = arguments
    random_source = Random(process_seed)
    family = template_family_named(blueprint.template_family)
    process_directory = output_directory / "documentos" / blueprint.identifier_prefix
    process_directory.mkdir(parents=True, exist_ok=True)
    document_records = []
    gold_documents = {}
    for plan in blueprint.plans:
        draft = family.render(plan, random_source)
        pdf_bytes = render_text_pdf(draft, plan.slots["sei_number"])
        was_scanned = random_source.random() < SCAN_RATE
        if was_scanned:
            pdf_bytes = convert_to_scanned_pdf(pdf_bytes, random_source)
        file_name = f"{plan.document_id}.pdf"
        (process_directory / file_name).write_bytes(pdf_bytes)
        title = draft.title if draft.title and random_source.random() >= GENERIC_TITLE_RATE else None
        document_records.append(
            {
                "document_id": plan.document_id,
                "declared_title": title or random_source.choice(GENERIC_TITLES),
                "path": str(Path("documentos") / blueprint.identifier_prefix / file_name),
                "sha256": hashlib.sha256(pdf_bytes).hexdigest(),
            }
        )
        gold_documents[plan.document_id] = {
            "document_type": plan.document_type.value,
            "was_scanned": was_scanned,
            "fields": expected_fields(plan),
        }
    return {
        "manifest": {
            "process_number": blueprint.process_number,
            "category": blueprint.category.value,
            "organ_name": blueprint.organ.name,
            "nucleus_code": blueprint.organ.nucleus_code,
            "documents": document_records,
        },
        "gold": {
            "process_number": blueprint.process_number,
            "category": blueprint.category.value,
            "template_family": blueprint.template_family,
            "complexity": blueprint.complexity,
            "irregularities": list(blueprint.irregularities),
            "distractors": blueprint.distractors,
            "documents": gold_documents,
        },
    }


def _plan_blueprints(request: CorpusRequest) -> list[tuple[ProcessBlueprint, int]]:
    planner = Random(request.seed)
    categories = [category for category, count in request.counts.items() for _ in range(count)]
    planner.shuffle(categories)
    earlier_invoices: list[dict[str, Any]] = []
    planned = []
    for index, category in enumerate(categories, start=1):
        family = request.template_families[index % len(request.template_families)]
        blueprint = build_blueprint(index, category, family, planner, request.irregularity_rate, earlier_invoices)
        planned.append((blueprint, planner.randint(0, 2**31)))
    return planned


def generate_corpus(request: CorpusRequest, root: Path, workers: int = 6) -> Path:
    output_directory = root / request.name
    (output_directory / "documentos").mkdir(parents=True, exist_ok=True)
    arguments = [(blueprint, seed, output_directory) for blueprint, seed in _plan_blueprints(request)]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(_render_process, arguments, chunksize=8))
    with (output_directory / "manifesto.jsonl").open("w", encoding="utf-8") as manifest:
        for result in results:
            manifest.write(json.dumps(result["manifest"], ensure_ascii=False) + "\n")
    with (output_directory / "gabarito.jsonl").open("w", encoding="utf-8") as gold:
        for result in results:
            gold.write(json.dumps(result["gold"], ensure_ascii=False) + "\n")
    return output_directory
