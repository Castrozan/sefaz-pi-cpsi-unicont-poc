from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from decimal import Decimal
from random import Random
from typing import Any

from unicont_poc.corpus.contract import DocumentPlan
from unicont_poc.corpus.processes.identities import Organ, PERSON_FIRST_NAMES, PERSON_LAST_NAMES, synthetic_cnpj
from unicont_poc.domain import DocumentType, ProcessCategory


@dataclass
class ProcessBlueprint:
    process_number: str
    category: ProcessCategory
    organ: Organ
    template_family: str
    irregularities: tuple[str, ...]
    complexity: str
    plans: list[DocumentPlan] = field(default_factory=list)
    distractors: list[str] = field(default_factory=list)

    @property
    def identifier_prefix(self) -> str:
        return self.process_number.replace(".", "").replace("/", "").replace("-", "")


class PlanWriter:
    def __init__(self, blueprint: ProcessBlueprint, random_source: Random) -> None:
        self.blueprint = blueprint
        self.random_source = random_source
        self.next_sei_number = random_source.randint(5_000_000, 9_000_000)

    def add(self, document_type: DocumentType, **slots: Any) -> None:
        self.next_sei_number += self.random_source.randint(1, 40)
        complete_slots = {
            "process_number": self.blueprint.process_number,
            "organ_name": self.blueprint.organ.name,
            "organ_cnpj": self.blueprint.organ.cnpj,
            "sei_number": str(self.next_sei_number),
            **slots,
        }
        self.blueprint.plans.append(DocumentPlan("", document_type, complete_slots))

    def add_routine_paperwork(self, count: int, anchor_date: date, party_name: str, reference_amount: Decimal) -> None:
        random_source = self.random_source
        for sequence_number in range(1, count + 1):
            mentions_unrelated_figures = random_source.random() < 0.35
            self.add(
                random_source.choice((DocumentType.DESPACHO, DocumentType.OFICIO)),
                issue_date=anchor_date - timedelta(days=random_source.randint(0, 25)),
                signer_name=person_name(random_source),
                signer_role=random_source.choice(("Chefe de Gabinete", "Diretor Administrativo", "Assessor Técnico")),
                recipient=random_source.choice(
                    ("Núcleo de Controle Interno", "Gerência Financeira", "Protocolo Geral")
                ),
                subject_kind=random_source.choice(("encaminhamento", "instrucao", "ciencia", "providencias")),
                supplier_name=party_name,
                unrelated_amount=reference_amount * random_source.randint(2, 9) if mentions_unrelated_figures else None,
                unrelated_cnpj=synthetic_cnpj(random_source) if mentions_unrelated_figures else None,
                sequence_number=sequence_number,
            )

    def finish(self) -> None:
        anchor, *remaining = self.blueprint.plans
        self.random_source.shuffle(remaining)
        self.blueprint.plans = [
            replace(plan, document_id=f"{self.blueprint.identifier_prefix}-{position:03d}")
            for position, plan in enumerate([anchor, *remaining], start=1)
        ]


def person_name(random_source: Random) -> str:
    return (
        f"{random_source.choice(PERSON_FIRST_NAMES)} "
        f"{random_source.choice(PERSON_LAST_NAMES)} {random_source.choice(PERSON_LAST_NAMES)}"
    )


def money(random_source: Random, minimum: int, maximum: int) -> Decimal:
    return Decimal(random_source.randint(minimum * 100, maximum * 100)) / 100


def percentage_of(amount: Decimal, percent: int) -> Decimal:
    return (amount * Decimal(percent) / 100).quantize(Decimal("0.01"))
