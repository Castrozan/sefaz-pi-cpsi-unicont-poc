from unicont_poc.analysis.extractors import extract_fields
from unicont_poc.analysis.process_view import ProcessView
from unicont_poc.domain import (
    AdministrativeProcess,
    ClassifiedDocument,
    DocumentType,
    PageText,
    ProcessCategory,
    SourceDocument,
)

PROCESS_NUMBER = "90001.000001/2026-11"


def classified(document_type: DocumentType, text: str, document_id: str = "d-001") -> ClassifiedDocument:
    source = SourceDocument(document_id, "Anexo", "0" * 64, (PageText(1, text),), False)
    document = ClassifiedDocument(source, document_type, 1.0, "regra")
    extract_fields(document)
    return document


def view_with(category: ProcessCategory, documents: list[ClassifiedDocument]) -> ProcessView:
    process = AdministrativeProcess(
        PROCESS_NUMBER, category, "Órgão Sintético 01", "NCI-01", tuple(document.document for document in documents)
    )
    return ProcessView(process, documents)


def regular_payment_documents(paid: str = "1.000,00", committed: str = "2.000,00") -> list[ClassifiedDocument]:
    return [
        classified(
            DocumentType.CONTRATO,
            "CONTRATADA: Fornecedora, CNPJ 11.222.333/0001-81. O presente contrato tem por objeto limpeza predial. "
            "Valor global: R$ 50.000,00.",
            "d-001",
        ),
        classified(
            DocumentType.NOTA_FISCAL,
            "Nota fiscal nº 12345 Emitente: Fornecedora – CNPJ 11.222.333/0001-81 Data de emissão: 10/03/2026 "
            "Discriminação: limpeza predial. Valor total da nota: R$ 1.000,00",
            "d-002",
        ),
        classified(DocumentType.NOTA_EMPENHO, f"Data de emissão: 01/03/2026 Valor empenhado: R$ {committed}", "d-003"),
        classified(DocumentType.ORDEM_PAGAMENTO, f"Data de pagamento: 20/03/2026 Valor pago: R$ {paid}", "d-004"),
        classified(DocumentType.CERTIDAO_FEDERAL, "Válida até 30/03/2026.", "d-005"),
        classified(DocumentType.CERTIDAO_FGTS, "Válida até 30/03/2026.", "d-006"),
        classified(DocumentType.CERTIDAO_TRABALHISTA, "Válida até 30/03/2026.", "d-007"),
        classified(DocumentType.ATESTO, "Atesto o recebimento integral.", "d-008"),
    ]
