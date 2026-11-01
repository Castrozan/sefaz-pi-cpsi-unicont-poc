from __future__ import annotations

import re

from unicont_poc.analysis.parsing import fold
from unicont_poc.analysis.process_view import ProcessView, SemanticVerdict, document_evidence
from unicont_poc.analysis.review.review_contract import ReviewAnswer
from unicont_poc.domain import CATEGORY_LABELS, CheckStatus, ClassifiedDocument, DocumentType

METHOD = "heuristica"
EXECUTION_EXCEPTION_PATTERN = r"observacao|nao fo(i|ram)|apenas|parcial|interdit|faltando|inferior|indisponive|a menos"
ADVERSE_OPINION_PATTERN = r"desfavoravel|condicionad"
STOPWORDS = {"prestacao", "servicos", "fornecimento", "aquisicao", "contratacao", "execucao", "para", "unidades"}


def _significant_words(text: str) -> set[str]:
    return {word for word in re.findall(r"[a-z]{5,}", fold(text)) if word not in STOPWORDS}


def _overlap_verdict(first_text: str, second_text: str, document: ClassifiedDocument, subject: str) -> SemanticVerdict:
    evidence = (document_evidence(document),)
    if _significant_words(first_text) & _significant_words(second_text):
        return SemanticVerdict(CheckStatus.CONFORME, f"{subject} com termos em comum.", evidence, METHOD)
    return SemanticVerdict(CheckStatus.NAO_CONFORME, f"{subject} sem termos em comum.", evidence, METHOD)


def _pattern_verdict(document: ClassifiedDocument, pattern: str, subject: str) -> SemanticVerdict:
    evidence = (document_evidence(document),)
    if re.search(pattern, fold(document.document.canonical_text)):
        return SemanticVerdict(CheckStatus.NAO_CONFORME, f"{subject}: termo de alerta encontrado.", evidence, METHOD)
    return SemanticVerdict(CheckStatus.CONFORME, f"{subject}: sem termo de alerta.", evidence, METHOD)


def _payment_verdicts(view: ProcessView) -> dict[str, SemanticVerdict]:
    verdicts = {}
    invoice, contract = view.first(DocumentType.NOTA_FISCAL), view.first(DocumentType.CONTRATO)
    if invoice is None:
        verdicts["PAG-10"] = SemanticVerdict(CheckStatus.PREJUDICADO, "Falta a nota fiscal.", (), METHOD)
    elif contract and invoice.value("description") and contract.value("object_text"):
        verdicts["PAG-10"] = _overlap_verdict(
            invoice.value("description"), contract.value("object_text"), invoice, "Nota e contrato"
        )
    attestation = view.first(DocumentType.ATESTO)
    if attestation is None:
        verdicts["PAG-11"] = SemanticVerdict(CheckStatus.PREJUDICADO, "Falta o atesto.", (), METHOD)
    else:
        verdicts["PAG-11"] = _pattern_verdict(attestation, EXECUTION_EXCEPTION_PATTERN, "Atesto")
    return verdicts


def _contracting_verdicts(view: ProcessView) -> dict[str, SemanticVerdict]:
    verdicts = {}
    opinion = view.first(DocumentType.PARECER_JURIDICO)
    if opinion is None:
        verdicts["CON-08"] = SemanticVerdict(CheckStatus.PREJUDICADO, "Falta o parecer.", (), METHOD)
    else:
        verdicts["CON-08"] = _pattern_verdict(opinion, ADVERSE_OPINION_PATTERN, "Parecer")
    terms, contract = view.first(DocumentType.TERMO_REFERENCIA), view.first(DocumentType.CONTRATO)
    if terms is None:
        verdicts["CON-09"] = SemanticVerdict(CheckStatus.PREJUDICADO, "Falta o termo de referência.", (), METHOD)
    elif contract and terms.value("object_text") and contract.value("object_text"):
        verdicts["CON-09"] = _overlap_verdict(
            terms.value("object_text"), contract.value("object_text"), contract, "Contrato e termo de referência"
        )
    return verdicts


def _accountability_verdicts(view: ProcessView) -> dict[str, SemanticVerdict]:
    plan, listing = view.first(DocumentType.PLANO_TRABALHO), view.first(DocumentType.RELACAO_PAGAMENTOS)
    if not plan or not listing or not listing.value("expenses"):
        return {}
    plan_words = _significant_words(plan.document.canonical_text)
    for row in listing.value("expenses"):
        if not _significant_words(row["line"]) & plan_words:
            return {
                "PRE-07": SemanticVerdict(
                    CheckStatus.NAO_CONFORME, "Despesa sem termos do plano.", (document_evidence(listing),), METHOD
                )
            }
    return {
        "PRE-07": SemanticVerdict(
            CheckStatus.CONFORME, "Despesas com termos do plano.", (document_evidence(listing),), METHOD
        )
    }


class RuleOnlyReview:
    def review(self, view: ProcessView) -> ReviewAnswer:
        category = CATEGORY_LABELS[view.process.category].lower()
        summary = (
            f"Processo de {category} do {view.process.organ_name}, com {len(view.documents)} documentos. "
            "Resumo extrativo gerado sem modelo de linguagem."
        )
        verdict_builders = {"pag": _payment_verdicts, "con": _contracting_verdicts, "pre": _accountability_verdicts}
        return ReviewAnswer(summary, verdict_builders[view.process.category.value[:3]](view))
