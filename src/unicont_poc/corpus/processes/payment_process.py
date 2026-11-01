from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from random import Random
from typing import Any

from unicont_poc.corpus.processes.blueprint import PlanWriter, ProcessBlueprint, money, person_name
from unicont_poc.corpus.processes.identities import SUPPLIER_NAMES, synthetic_cnpj
from unicont_poc.corpus.processes.object_scenarios import OBJECT_SCENARIOS, ObjectScenario
from unicont_poc.corpus.processes.payment_certificates import add_certificates
from unicont_poc.corpus.processes.payment_commitments import CommitmentTerms, add_commitments
from unicont_poc.domain import DocumentType

PAPERWORK_BY_COMPLEXITY = {"baixa": 2, "media": 6, "alta": 14}


@dataclass(frozen=True)
class PaymentParties:
    supplier_name: str
    supplier_cnpj: str
    fiscal_name: str
    contract_number: str


def _add_invoices(
    writer: PlanWriter,
    parties: PaymentParties,
    scenario: ObjectScenario,
    invoice_amounts: list[Decimal],
    invoice_date: date,
    sibling_invoice: dict[str, Any] | None,
) -> list[str]:
    irregular = set(writer.blueprint.irregularities)
    random_source = writer.random_source
    if "PAG-01" in irregular:
        return [str(random_source.randint(1000, 899_999))]
    invoice_cnpj = synthetic_cnpj(random_source) if "PAG-07" in irregular else parties.supplier_cnpj
    description = random_source.choice(
        scenario.incompatible_invoice_descriptions if "PAG-10" in irregular else scenario.invoice_descriptions
    )
    invoice_numbers: list[str] = []
    for index, amount in enumerate(invoice_amounts):
        invoice_number = str(random_source.randint(1000, 899_999))
        if sibling_invoice is not None and index == 0:
            invoice_number = sibling_invoice["invoice_number"]
        invoice_numbers.append(invoice_number)
        writer.add(
            DocumentType.NOTA_FISCAL,
            invoice_number=invoice_number,
            supplier_name=parties.supplier_name,
            supplier_cnpj=invoice_cnpj,
            description=description,
            amount=amount,
            issue_date=invoice_date + timedelta(days=index),
        )
    return invoice_numbers


def _add_attestation(
    writer: PlanWriter, parties: PaymentParties, scenario: ObjectScenario, invoice_numbers: list[str], issue_date: date
) -> None:
    irregular = set(writer.blueprint.irregularities)
    random_source = writer.random_source
    if "PAG-02" in irregular:
        return
    statement_kind, exception_detail = "sem_ressalva", ""
    if "PAG-11" in irregular:
        statement_kind, exception_detail = "ressalva_execucao", random_source.choice(scenario.execution_exceptions)
    elif random_source.random() < 0.25:
        statement_kind, exception_detail = "ressalva_afastada", random_source.choice(scenario.resolved_exceptions)
        writer.blueprint.distractors.append("atesto_com_ressalva_afastada")
    writer.add(
        DocumentType.ATESTO,
        invoice_numbers=invoice_numbers,
        attesting_name=parties.fiscal_name,
        attesting_role="Fiscal do Contrato",
        statement_kind=statement_kind,
        exception_detail=exception_detail,
        issue_date=issue_date,
        contract_number=parties.contract_number,
        service_summary=scenario.object_text,
    )


def build_payment_process(
    blueprint: ProcessBlueprint, random_source: Random, sibling_invoice: dict[str, Any] | None
) -> None:
    writer = PlanWriter(blueprint, random_source)
    irregular = set(blueprint.irregularities)
    scenario = random_source.choice(OBJECT_SCENARIOS)
    parties = PaymentParties(
        supplier_name=sibling_invoice["supplier_name"] if sibling_invoice else random_source.choice(SUPPLIER_NAMES),
        supplier_cnpj=sibling_invoice["supplier_cnpj"] if sibling_invoice else synthetic_cnpj(random_source),
        fiscal_name=person_name(random_source),
        contract_number=f"{random_source.randint(1, 240):03d}/2026",
    )
    payment_date = date(2026, random_source.randint(3, 9), random_source.randint(1, 28))
    invoice_date = payment_date - timedelta(days=random_source.randint(6, 20))
    commitment_date = invoice_date - timedelta(days=random_source.randint(5, 40))
    if "PAG-08" in irregular:
        commitment_date = invoice_date + timedelta(days=random_source.randint(2, 12))

    invoice_amounts = [money(random_source, 3_000, 45_000) for _ in range(random_source.choices((1, 2), (80, 20))[0])]
    if sibling_invoice is not None:
        invoice_amounts[0] = sibling_invoice["amount"]
    invoice_total = sum(invoice_amounts, Decimal(0))
    paid_amount = invoice_total + (money(random_source, 150, 4_000) if "PAG-05" in irregular else Decimal(0))

    writer.add(
        DocumentType.CONTRATO,
        contract_number=parties.contract_number,
        supplier_name=parties.supplier_name,
        supplier_cnpj=parties.supplier_cnpj,
        object_text=scenario.object_text,
        amount=money(random_source, 60_000, 900_000),
        start_date=date(2026, 1, random_source.randint(5, 25)),
        end_date=date(2026, 12, 31),
        fiscal_name=parties.fiscal_name,
        issue_date=date(2026, 1, 4),
        signer_name=person_name(random_source),
    )
    commitment_number = add_commitments(
        writer,
        CommitmentTerms(parties.supplier_name, parties.supplier_cnpj, scenario.object_text, commitment_date),
        paid_amount,
    )
    invoice_numbers = _add_invoices(writer, parties, scenario, invoice_amounts, invoice_date, sibling_invoice)
    attestation_date = invoice_date + timedelta(days=random_source.randint(2, 5))
    _add_attestation(writer, parties, scenario, invoice_numbers, attestation_date)
    add_certificates(writer, parties.supplier_name, parties.supplier_cnpj, payment_date)
    writer.add(
        DocumentType.LIQUIDACAO,
        settlement_number=f"2026NL{random_source.randint(100, 9999):05d}",
        commitment_number=commitment_number,
        invoice_numbers=invoice_numbers,
        supplier_name=parties.supplier_name,
        supplier_cnpj=parties.supplier_cnpj,
        amount=paid_amount,
        issue_date=payment_date - timedelta(days=random_source.randint(1, 4)),
    )
    writer.add(
        DocumentType.ORDEM_PAGAMENTO,
        payment_order_number=f"2026OB{random_source.randint(100, 9999):05d}",
        supplier_name=parties.supplier_name,
        supplier_cnpj=parties.supplier_cnpj,
        amount=paid_amount,
        issue_date=payment_date,
        bank_account=f"{random_source.randint(1000, 9999)}-{random_source.randint(0, 9)}",
    )
    paperwork = PAPERWORK_BY_COMPLEXITY[blueprint.complexity] + random_source.randint(0, 3)
    writer.add_routine_paperwork(paperwork, payment_date, parties.supplier_name, invoice_total)
    writer.finish()
