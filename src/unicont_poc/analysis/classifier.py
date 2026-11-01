from __future__ import annotations

import re
from dataclasses import dataclass

from unicont_poc.analysis.parsing import fold
from unicont_poc.domain import ClassifiedDocument, DocumentType, SourceDocument

HEADING_WINDOW = 260
MINIMUM_CONFIDENT_SCORE = 3
MINIMUM_CONFIDENCE = 0.6


@dataclass(frozen=True)
class TypeSignature:
    document_type: DocumentType
    heading: str
    body: str = r"(?!x)x"


SIGNATURES: tuple[TypeSignature, ...] = (
    TypeSignature(DocumentType.NOTA_FISCAL, r"nota fiscal|nfs-?e|nf-?e|danfe", r"tomador|discriminacao"),
    TypeSignature(DocumentType.ATESTO, r"\batesto\b|atestamos|termo de recebimento", r"\batesto que\b|recebimento"),
    TypeSignature(DocumentType.NOTA_EMPENHO, r"nota de empenho|\bempenho n", r"valor empenhado|natureza da despesa"),
    TypeSignature(DocumentType.LIQUIDACAO, r"liquidacao", r"valor liquidado"),
    TypeSignature(DocumentType.ORDEM_PAGAMENTO, r"ordem bancaria|ordem de pagamento", r"favorecido|domicilio bancario"),
    TypeSignature(
        DocumentType.CONTRATO, r"\bcontrato n|termo de contrato|instrumento contratual", r"contratante.*contratada"
    ),
    TypeSignature(DocumentType.CERTIDAO_FEDERAL, r"tributos federais|divida ativa da uniao|receita federal"),
    TypeSignature(DocumentType.CERTIDAO_FGTS, r"\bfgts\b|\bcrf\b|fundo de garantia"),
    TypeSignature(DocumentType.CERTIDAO_TRABALHISTA, r"debitos trabalhistas|\bcndt\b|justica do trabalho"),
    TypeSignature(
        DocumentType.ESTUDO_TECNICO_PRELIMINAR, r"estudo tecnico preliminar|\betp\b", r"descricao da necessidade"
    ),
    TypeSignature(DocumentType.TERMO_REFERENCIA, r"termo de referencia", r"modelo de execucao"),
    TypeSignature(DocumentType.PESQUISA_PRECOS, r"pesquisa de precos|mapa de precos|cotacao|cotacoes", r"fornecedor 1"),
    TypeSignature(DocumentType.PROPOSTA, r"proposta comercial|proposta de precos", r"proponente"),
    TypeSignature(DocumentType.PARECER_JURIDICO, r"parecer", r"opina-se|procuradoria"),
    TypeSignature(DocumentType.PORTARIA_FISCAL, r"\bportaria\b", r"fica designad|fiscal do contrato"),
    TypeSignature(DocumentType.ART, r"responsabilidade tecnica|\bart\b", r"\bcrea\b"),
    TypeSignature(DocumentType.TERMO_CONVENIO, r"termo de convenio|\bconvenio n", r"concedente"),
    TypeSignature(DocumentType.PLANO_TRABALHO, r"plano de trabalho", r"itens de despesa"),
    TypeSignature(
        DocumentType.RELATORIO_EXECUCAO, r"relatorio de execucao|relatorio de cumprimento", r"metas pactuadas"
    ),
    TypeSignature(
        DocumentType.RELACAO_PAGAMENTOS, r"relacao de pagamentos|demonstrativo de despesas", r"total declarado"
    ),
    TypeSignature(DocumentType.EXTRATO_BANCARIO, r"extrato", r"saldo inicial|saldo final"),
    TypeSignature(
        DocumentType.COMPROVANTE_DEVOLUCAO,
        r"devolucao de saldo|comprovante de devolucao|recolhimento de saldo",
        r"valor devolvido",
    ),
    TypeSignature(DocumentType.DESPACHO, r"\bdespacho\b"),
    TypeSignature(DocumentType.OFICIO, r"\boficio\b"),
)


def score_document(document: SourceDocument) -> dict[DocumentType, int]:
    body = fold(document.canonical_text)
    heading = body[:HEADING_WINDOW]
    declared_title = fold(document.declared_title)
    scores: dict[DocumentType, int] = {}
    for signature in SIGNATURES:
        score = 0
        if re.search(signature.heading, heading):
            score += 3
        if re.search(signature.heading, declared_title):
            score += 3
        if re.search(signature.body, body):
            score += 2
        if score:
            scores[signature.document_type] = score
    return scores


def classify_document(document: SourceDocument) -> ClassifiedDocument:
    ranked = sorted(score_document(document).items(), key=lambda item: item[1], reverse=True)
    if not ranked:
        return ClassifiedDocument(document, DocumentType.OFICIO, 0.0, "regra")
    best_type, best_score = ranked[0]
    runner_up_score = ranked[1][1] if len(ranked) > 1 else 0
    confidence = best_score / (best_score + runner_up_score)
    if best_score < MINIMUM_CONFIDENT_SCORE:
        confidence = min(confidence, MINIMUM_CONFIDENCE - 0.01)
    return ClassifiedDocument(document, best_type, round(confidence, 3), "regra")


def needs_language_review(classified: ClassifiedDocument) -> bool:
    return classified.confidence < MINIMUM_CONFIDENCE
