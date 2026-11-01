from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from unicont_poc.corpus.processes.blueprint import PlanWriter, money
from unicont_poc.domain import DocumentType


@dataclass(frozen=True)
class CommitmentTerms:
    supplier_name: str
    supplier_cnpj: str
    description: str
    issue_date: date


def _commitment_number(writer: PlanWriter) -> str:
    return f"2026NE{writer.random_source.randint(100, 9999):05d}"


def _add_commitment(
    writer: PlanWriter, terms: CommitmentTerms, number: str, amount: Decimal, issue_date: date, kind: str
) -> None:
    writer.add(
        DocumentType.NOTA_EMPENHO,
        commitment_number=number,
        supplier_name=terms.supplier_name,
        supplier_cnpj=terms.supplier_cnpj,
        amount=amount,
        budget_line=f"3.3.90.39.{writer.random_source.randint(10, 99)}",
        description=terms.description,
        issue_date=issue_date,
        kind=kind,
    )


def add_commitments(writer: PlanWriter, terms: CommitmentTerms, paid_amount: Decimal) -> str:
    random_source = writer.random_source
    is_overdrawn = "PAG-06" in writer.blueprint.irregularities
    covered_amount = paid_amount + money(random_source, 500, 30_000)
    if is_overdrawn:
        covered_amount = paid_amount - money(random_source, 200, 2_500)
    number = _commitment_number(writer)
    if is_overdrawn or random_source.random() >= 0.2:
        _add_commitment(writer, terms, number, covered_amount, terms.issue_date, "original")
        return number
    original_share = (covered_amount * Decimal("0.6")).quantize(Decimal("0.01"))
    writer.blueprint.distractors.append("empenho_com_reforco")
    _add_commitment(writer, terms, number, original_share, terms.issue_date, "original")
    reinforcement_date = terms.issue_date + timedelta(days=random_source.randint(1, 4))
    _add_commitment(
        writer, terms, _commitment_number(writer), covered_amount - original_share, reinforcement_date, "reforco"
    )
    return number
