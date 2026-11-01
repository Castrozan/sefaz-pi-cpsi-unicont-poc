from __future__ import annotations

from datetime import date, timedelta

from unicont_poc.corpus.processes.blueprint import PlanWriter
from unicont_poc.domain import DocumentType

CERTIFICATE_TYPES = (DocumentType.CERTIDAO_FEDERAL, DocumentType.CERTIDAO_FGTS, DocumentType.CERTIDAO_TRABALHISTA)


def _add_certificate(
    writer: PlanWriter,
    document_type: DocumentType,
    supplier_name: str,
    supplier_cnpj: str,
    issue_date: date,
    valid_until: date,
) -> None:
    writer.add(
        document_type,
        supplier_name=supplier_name,
        supplier_cnpj=supplier_cnpj,
        issue_date=issue_date,
        valid_until=valid_until,
        certificate_code=f"{writer.random_source.randint(10**11, 10**12):X}",
    )


def add_certificates(writer: PlanWriter, supplier_name: str, supplier_cnpj: str, payment_date: date) -> None:
    random_source = writer.random_source
    irregular = set(writer.blueprint.irregularities)
    missing = random_source.choice(CERTIFICATE_TYPES) if "PAG-03" in irregular else None
    expired = random_source.choice(CERTIFICATE_TYPES) if "PAG-04" in irregular else None
    renewed = random_source.choice(CERTIFICATE_TYPES) if not expired and random_source.random() < 0.25 else None
    if renewed is missing:
        renewed = None
    if renewed:
        writer.blueprint.distractors.append("certidao_renovada")
    for document_type in CERTIFICATE_TYPES:
        if document_type is missing:
            continue
        if document_type is expired:
            valid_until = payment_date - timedelta(days=random_source.randint(1, 20))
            _add_certificate(
                writer, document_type, supplier_name, supplier_cnpj, valid_until - timedelta(days=30), valid_until
            )
            continue
        if document_type is renewed:
            previous_validity = payment_date - timedelta(days=random_source.randint(10, 40))
            _add_certificate(
                writer,
                document_type,
                supplier_name,
                supplier_cnpj,
                previous_validity - timedelta(days=30),
                previous_validity,
            )
        _add_certificate(
            writer,
            document_type,
            supplier_name,
            supplier_cnpj,
            payment_date - timedelta(days=random_source.randint(3, 25)),
            payment_date + timedelta(days=random_source.randint(5, 60)),
        )
