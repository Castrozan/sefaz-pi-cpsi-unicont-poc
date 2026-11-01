from __future__ import annotations

from datetime import date, timedelta
from random import Random

from unicont_poc.corpus.blueprint import PlanWriter, ProcessBlueprint, money, percentage_of, person_name
from unicont_poc.corpus.identities import SUPPLIER_NAMES, synthetic_cnpj
from unicont_poc.corpus.object_scenarios import OBJECT_SCENARIOS, ObjectScenario
from unicont_poc.domain import DocumentType

PAPERWORK_BY_COMPLEXITY = {"baixa": 6, "media": 16, "alta": 34}


def _add_legal_opinion(writer: PlanWriter, scenario: ObjectScenario, issue_date: date) -> None:
    irregular = set(writer.blueprint.irregularities)
    random_source = writer.random_source
    if "CON-03" in irregular:
        return
    opinion_kind, opinion_detail = "favoravel", ""
    if "CON-08" in irregular:
        opinion_kind = random_source.choice(("desfavoravel", "ressalva_pendente"))
        opinion_detail = random_source.choice(scenario.legal_objections)
    elif random_source.random() < 0.3:
        opinion_kind, opinion_detail = (
            "recomendacao_atendida",
            random_source.choice(scenario.resolved_legal_recommendations),
        )
        writer.blueprint.distractors.append("parecer_com_recomendacao_atendida")
    writer.add(
        DocumentType.PARECER_JURIDICO,
        opinion_kind=opinion_kind,
        opinion_detail=opinion_detail,
        opinion_number=f"{random_source.randint(10, 999)}/2026",
        issue_date=issue_date,
        signer_name=person_name(random_source),
    )


def _add_planning_documents(writer: PlanWriter, scenario: ObjectScenario, estimated_amount, anchor_date: date) -> None:
    irregular = set(writer.blueprint.irregularities)
    random_source = writer.random_source
    if "CON-01" not in irregular:
        writer.add(
            DocumentType.ESTUDO_TECNICO_PRELIMINAR,
            need_text=scenario.need_text,
            object_text=scenario.object_text,
            estimated_amount=estimated_amount,
            issue_date=anchor_date - timedelta(days=60),
            signer_name=person_name(random_source),
        )
    if "CON-02" not in irregular:
        writer.add(
            DocumentType.TERMO_REFERENCIA,
            object_text=scenario.object_text,
            estimated_amount=estimated_amount,
            issue_date=anchor_date - timedelta(days=50),
            signer_name=person_name(random_source),
        )
    quote_count = random_source.choice((1, 2)) if "CON-04" in irregular else random_source.choice((3, 3, 4, 5))
    quotes = [
        {
            "supplier_name": random_source.choice(SUPPLIER_NAMES),
            "supplier_cnpj": synthetic_cnpj(random_source),
            "amount": percentage_of(estimated_amount, random_source.randint(94, 108)),
        }
        for _ in range(quote_count)
    ]
    writer.add(
        DocumentType.PESQUISA_PRECOS,
        quotes=quotes,
        estimated_amount=estimated_amount,
        issue_date=anchor_date - timedelta(days=40),
        signer_name=person_name(random_source),
    )


def build_contracting_process(blueprint: ProcessBlueprint, random_source: Random) -> None:
    writer = PlanWriter(blueprint, random_source)
    irregular = set(blueprint.irregularities)
    scenario = random_source.choice(OBJECT_SCENARIOS)
    supplier_name = random_source.choice(SUPPLIER_NAMES)
    supplier_cnpj = synthetic_cnpj(random_source)
    estimated_amount = money(random_source, 40_000, 2_400_000)
    contract_percent = random_source.randint(103, 124) if "CON-05" in irregular else random_source.randint(86, 99)
    contract_amount = percentage_of(estimated_amount, contract_percent)
    anchor_date = date(2026, random_source.randint(2, 9), random_source.randint(1, 28))
    fiscal_name = person_name(random_source)
    contract_number = f"{random_source.randint(1, 240):03d}/2026"

    _add_planning_documents(writer, scenario, estimated_amount, anchor_date)
    writer.add(
        DocumentType.PROPOSTA,
        supplier_name=supplier_name,
        supplier_cnpj=synthetic_cnpj(random_source) if "CON-07" in irregular else supplier_cnpj,
        object_text=scenario.object_text,
        amount=contract_amount,
        issue_date=anchor_date - timedelta(days=25),
    )
    _add_legal_opinion(writer, scenario, anchor_date - timedelta(days=15))
    writer.add(
        DocumentType.CONTRATO,
        contract_number=contract_number,
        supplier_name=supplier_name,
        supplier_cnpj=supplier_cnpj,
        object_text=random_source.choice(scenario.divergent_object_texts)
        if "CON-09" in irregular
        else scenario.object_text,
        amount=contract_amount,
        start_date=anchor_date,
        end_date=anchor_date + timedelta(days=365),
        fiscal_name="" if "CON-06" in irregular else fiscal_name,
        issue_date=anchor_date,
        signer_name=person_name(random_source),
    )
    if "CON-06" not in irregular:
        writer.add(
            DocumentType.PORTARIA_FISCAL,
            ordinance_number=f"{random_source.randint(10, 999)}/2026",
            fiscal_name=fiscal_name,
            contract_number=contract_number,
            issue_date=anchor_date + timedelta(days=random_source.randint(1, 6)),
            signer_name=person_name(random_source),
        )
    if scenario.requires_technical_responsibility:
        writer.add(
            DocumentType.ART,
            responsible_name=person_name(random_source),
            registration_number=f"{random_source.randint(100000, 999999)}-PI",
            art_number=f"PI{random_source.randint(10**9, 10**10)}",
            description=scenario.object_text,
            issue_date=anchor_date + timedelta(days=2),
        )
    paperwork = PAPERWORK_BY_COMPLEXITY[blueprint.complexity] + random_source.randint(0, 5)
    writer.add_routine_paperwork(paperwork, anchor_date, supplier_name, estimated_amount)
    writer.finish()
