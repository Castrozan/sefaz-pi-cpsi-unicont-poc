from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class ProcessCategory(StrEnum):
    PAGAMENTO = "pagamento"
    CONTRATACAO = "contratacao"
    PRESTACAO_DE_CONTAS = "prestacao_de_contas"


class DocumentType(StrEnum):
    NOTA_FISCAL = "nota_fiscal"
    ATESTO = "atesto"
    NOTA_EMPENHO = "nota_empenho"
    LIQUIDACAO = "liquidacao"
    ORDEM_PAGAMENTO = "ordem_pagamento"
    CONTRATO = "contrato"
    CERTIDAO_FEDERAL = "certidao_federal"
    CERTIDAO_FGTS = "certidao_fgts"
    CERTIDAO_TRABALHISTA = "certidao_trabalhista"
    ESTUDO_TECNICO_PRELIMINAR = "estudo_tecnico_preliminar"
    TERMO_REFERENCIA = "termo_referencia"
    PESQUISA_PRECOS = "pesquisa_precos"
    PROPOSTA = "proposta"
    PARECER_JURIDICO = "parecer_juridico"
    PORTARIA_FISCAL = "portaria_fiscal"
    ART = "art"
    TERMO_CONVENIO = "termo_convenio"
    PLANO_TRABALHO = "plano_trabalho"
    RELATORIO_EXECUCAO = "relatorio_execucao"
    RELACAO_PAGAMENTOS = "relacao_pagamentos"
    EXTRATO_BANCARIO = "extrato_bancario"
    COMPROVANTE_DEVOLUCAO = "comprovante_devolucao"
    DESPACHO = "despacho"
    OFICIO = "oficio"


DOCUMENT_TYPE_LABELS: dict[DocumentType, str] = {
    DocumentType.NOTA_FISCAL: "Nota fiscal",
    DocumentType.ATESTO: "Atesto de recebimento",
    DocumentType.NOTA_EMPENHO: "Nota de empenho",
    DocumentType.LIQUIDACAO: "Liquidação da despesa",
    DocumentType.ORDEM_PAGAMENTO: "Ordem de pagamento",
    DocumentType.CONTRATO: "Contrato",
    DocumentType.CERTIDAO_FEDERAL: "Certidão federal",
    DocumentType.CERTIDAO_FGTS: "Certificado do FGTS",
    DocumentType.CERTIDAO_TRABALHISTA: "Certidão trabalhista",
    DocumentType.ESTUDO_TECNICO_PRELIMINAR: "Estudo técnico preliminar",
    DocumentType.TERMO_REFERENCIA: "Termo de referência",
    DocumentType.PESQUISA_PRECOS: "Pesquisa de preços",
    DocumentType.PROPOSTA: "Proposta comercial",
    DocumentType.PARECER_JURIDICO: "Parecer jurídico",
    DocumentType.PORTARIA_FISCAL: "Portaria de designação de fiscal",
    DocumentType.ART: "Anotação de responsabilidade técnica",
    DocumentType.TERMO_CONVENIO: "Termo de convênio",
    DocumentType.PLANO_TRABALHO: "Plano de trabalho",
    DocumentType.RELATORIO_EXECUCAO: "Relatório de execução",
    DocumentType.RELACAO_PAGAMENTOS: "Relação de pagamentos",
    DocumentType.EXTRATO_BANCARIO: "Extrato bancário",
    DocumentType.COMPROVANTE_DEVOLUCAO: "Comprovante de devolução de saldo",
    DocumentType.DESPACHO: "Despacho",
    DocumentType.OFICIO: "Ofício",
}

CATEGORY_LABELS: dict[ProcessCategory, str] = {
    ProcessCategory.PAGAMENTO: "Pagamento",
    ProcessCategory.CONTRATACAO: "Contratação",
    ProcessCategory.PRESTACAO_DE_CONTAS: "Prestação de contas",
}


class CheckStatus(StrEnum):
    CONFORME = "conforme"
    NAO_CONFORME = "nao_conforme"
    NAO_VERIFICAVEL = "nao_verificavel"
    PREJUDICADO = "prejudicado"


class RiskLevel(StrEnum):
    BAIXO = "baixo"
    MEDIO = "medio"
    ALTO = "alto"


class ReviewState(StrEnum):
    AGUARDANDO_ANALISTA = "aguardando_analista"
    APROVADO = "aprovado"
    DEVOLVIDO = "devolvido"


@dataclass(frozen=True)
class PageText:
    page_number: int
    text: str

    @property
    def canonical_text(self) -> str:
        return " ".join(self.text.split())


@dataclass(frozen=True)
class SourceDocument:
    document_id: str
    declared_title: str
    sha256: str
    pages: tuple[PageText, ...]
    was_scanned: bool

    @property
    def canonical_text(self) -> str:
        return " ".join(page.canonical_text for page in self.pages)


@dataclass(frozen=True)
class AdministrativeProcess:
    process_number: str
    category: ProcessCategory
    organ_name: str
    nucleus_code: str
    documents: tuple[SourceDocument, ...]


@dataclass(frozen=True)
class Evidence:
    document_id: str
    page_number: int
    quote: str
    document_label: str = ""


@dataclass(frozen=True)
class CheckResult:
    code: str
    title: str
    legal_basis: str
    status: CheckStatus
    rationale: str
    method: str
    evidence: tuple[Evidence, ...] = ()


@dataclass(frozen=True)
class ExtractedField:
    value: object
    evidence: Evidence
    method: str = "regra"


@dataclass
class ClassifiedDocument:
    document: SourceDocument
    document_type: DocumentType
    confidence: float
    method: str
    fields: dict[str, ExtractedField] = field(default_factory=dict)

    @property
    def label(self) -> str:
        return DOCUMENT_TYPE_LABELS[self.document_type]

    def value(self, field_name: str) -> object | None:
        extracted = self.fields.get(field_name)
        return extracted.value if extracted else None

    def evidence_for(self, field_name: str) -> Evidence | None:
        extracted = self.fields.get(field_name)
        return extracted.evidence if extracted else None
