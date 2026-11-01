from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from random import Random

from unicont_poc.corpus.processes.blueprint import PlanWriter, ProcessBlueprint, money, person_name
from unicont_poc.corpus.processes.identities import SUPPLIER_NAMES, synthetic_cnpj
from unicont_poc.corpus.processes.object_scenarios import OBJECT_SCENARIOS, ObjectScenario
from unicont_poc.domain import DocumentType

PAPERWORK_BY_COMPLEXITY = {"baixa": 4, "media": 10, "alta": 22}


def _planned_expenses(
    random_source: Random, irregular: set[str], scenario: ObjectScenario, start_date: date, end_date: date
) -> list[dict]:
    expense_count = random_source.randint(4, 9)
    expenses = [
        {
            "date": start_date + timedelta(days=random_source.randint(5, (end_date - start_date).days - 5)),
            "supplier_name": random_source.choice(SUPPLIER_NAMES),
            "description": random_source.choice(scenario.invoice_descriptions),
            "amount": money(random_source, 800, 18_000),
        }
        for _ in range(expense_count)
    ]
    if "PRE-05" in irregular:
        expenses[random_source.randrange(expense_count)]["date"] = end_date + timedelta(
            days=random_source.randint(4, 40)
        )
    if "PRE-07" in irregular:
        expenses[random_source.randrange(expense_count)]["description"] = random_source.choice(
            scenario.incompatible_invoice_descriptions
        )
    return sorted(expenses, key=lambda expense: expense["date"])


def build_accountability_process(blueprint: ProcessBlueprint, random_source: Random) -> None:
    writer = PlanWriter(blueprint, random_source)
    irregular = set(blueprint.irregularities)
    scenario = random_source.choice(OBJECT_SCENARIOS)
    partner_name = f"Associação {random_source.choice(SUPPLIER_NAMES).split()[0]} de Desenvolvimento Comunitário"
    partner_cnpj = synthetic_cnpj(random_source)
    agreement_number = f"{random_source.randint(1, 90):03d}/2025"
    start_date = date(2025, random_source.randint(3, 8), random_source.randint(1, 28))
    end_date = start_date + timedelta(days=random_source.randint(240, 300))
    report_deadline = end_date + timedelta(days=60)

    expenses = _planned_expenses(random_source, irregular, scenario, start_date, end_date)
    spent_total = sum((expense["amount"] for expense in expenses), Decimal(0))
    leftover = money(random_source, 120, 9_000)
    if random_source.random() >= 0.7 and "PRE-03" not in irregular:
        leftover = Decimal("0.00")
        blueprint.distractors.append("sem_saldo_a_devolver")
    agreement_amount = spent_total + leftover
    declared_total = spent_total + (money(random_source, 300, 6_000) if "PRE-04" in irregular else Decimal(0))
    delivered_on = report_deadline - timedelta(days=random_source.randint(2, 30))
    if "PRE-06" in irregular:
        delivered_on = report_deadline + timedelta(days=random_source.randint(5, 45))

    writer.add(
        DocumentType.TERMO_CONVENIO,
        agreement_number=agreement_number,
        partner_name=partner_name,
        partner_cnpj=partner_cnpj,
        object_text=scenario.object_text,
        amount=agreement_amount,
        start_date=start_date,
        end_date=end_date,
        report_deadline=report_deadline,
        issue_date=start_date,
        signer_name=person_name(random_source),
    )
    writer.add(
        DocumentType.PLANO_TRABALHO,
        agreement_number=agreement_number,
        partner_name=partner_name,
        object_text=scenario.object_text,
        allowed_items=scenario.invoice_descriptions,
        amount=agreement_amount,
        issue_date=start_date,
    )
    if "PRE-01" not in irregular:
        writer.add(
            DocumentType.RELATORIO_EXECUCAO,
            agreement_number=agreement_number,
            partner_name=partner_name,
            partner_cnpj=partner_cnpj,
            object_text=scenario.object_text,
            delivered_on=delivered_on,
            issue_date=delivered_on,
            signer_name=person_name(random_source),
        )
    writer.add(
        DocumentType.RELACAO_PAGAMENTOS,
        agreement_number=agreement_number,
        partner_cnpj=partner_cnpj,
        expenses=expenses,
        declared_total=declared_total,
        delivered_on=delivered_on,
        issue_date=delivered_on - timedelta(days=2),
    )
    if "PRE-02" not in irregular:
        writer.add(
            DocumentType.EXTRATO_BANCARIO,
            agreement_number=agreement_number,
            partner_name=partner_name,
            opening_balance=agreement_amount,
            closing_balance=leftover if "PRE-03" in irregular else Decimal("0.00"),
            leftover=leftover,
            issue_date=end_date + timedelta(days=20),
        )
    if leftover > 0 and "PRE-03" not in irregular:
        writer.add(
            DocumentType.COMPROVANTE_DEVOLUCAO,
            agreement_number=agreement_number,
            partner_name=partner_name,
            amount=leftover,
            issue_date=end_date + timedelta(days=random_source.randint(5, 30)),
        )
    paperwork = PAPERWORK_BY_COMPLEXITY[blueprint.complexity] + random_source.randint(0, 4)
    writer.add_routine_paperwork(paperwork, end_date, partner_name, agreement_amount)
    writer.finish()
