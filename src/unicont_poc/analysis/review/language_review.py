from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from decimal import Decimal, InvalidOperation

from unicont_poc.analysis.review.language_prompt import SYSTEM_PROMPT, build_user_prompt
from unicont_poc.analysis.parsing import find_cnpjs
from unicont_poc.analysis.process_view import ProcessView, SemanticVerdict
from unicont_poc.analysis.review.review_contract import ReviewAnswer
from unicont_poc.corpus.catalog import checklist_for
from unicont_poc.domain import CheckStatus, ClassifiedDocument, DocumentType, Evidence, ExtractedField
from unicont_poc.ports import LanguageModel, LanguageRequest

METHOD = "modelo"
DATE_FIELDS = {"issue_date", "payment_date", "valid_until", "delivered_on", "report_deadline", "start_date", "end_date"}
AMOUNT_FIELDS = {"amount", "closing_balance"}


def _collapse(text: str) -> str:
    return " ".join(text.split())


def locate_quote(document: ClassifiedDocument, quote: str, label: str) -> Evidence | None:
    wanted = _collapse(quote)
    if not wanted:
        return None
    for page in document.document.pages:
        if wanted.casefold() in page.canonical_text.casefold():
            return Evidence(document.document.document_id, page.page_number, wanted, label)
    return None


def _parse_field_value(name: str, raw: str) -> object | None:
    try:
        if name in AMOUNT_FIELDS:
            return Decimal(str(raw).replace("R$", "").strip())
        if name in DATE_FIELDS:
            return date.fromisoformat(str(raw))
        if name == "quote_count":
            return int(raw)
        if name == "cnpj":
            matches = find_cnpjs(str(raw))
            return matches[0].value if matches else None
    except (InvalidOperation, ValueError):
        return None
    return str(raw).strip() or None


def _strip_json_fence(text: str) -> str:
    found = re.search(r"\{.*\}", text, re.DOTALL)
    return found.group() if found else "{}"


class LanguageModelReview:
    def __init__(self, language_model: LanguageModel) -> None:
        self.language_model = language_model

    def review(self, view: ProcessView) -> ReviewAnswer:
        user_prompt = build_user_prompt(view)
        reply = self.language_model.complete(LanguageRequest(SYSTEM_PROMPT, user_prompt))
        try:
            payload = json.loads(_strip_json_fence(reply.text))
        except json.JSONDecodeError:
            payload = {}
        documents = {document.document.document_id: document for document in view.documents}
        answer = ReviewAnswer(
            summary=str(payload.get("resumo", "")).strip() or "Resumo indisponível nesta análise.",
            semantic_verdicts={},
            model_identifier=reply.model_identifier,
            execution_mode=reply.execution_mode,
            prompt_sha256=hashlib.sha256((SYSTEM_PROMPT + user_prompt).encode()).hexdigest(),
        )
        self._read_verifications(view, payload, documents, answer)
        self._read_classifications(payload, documents, answer)
        self._read_fields(payload, documents, answer)
        return answer

    def _citations(self, entry: dict, documents: dict, answer: ReviewAnswer) -> tuple[Evidence, ...]:
        located = []
        for citation in entry.get("citacoes", []):
            document = documents.get(citation.get("document_id"))
            evidence = locate_quote(document, str(citation.get("trecho", "")), document.label) if document else None
            if evidence is None:
                answer.rejected_citations += 1
            else:
                located.append(evidence)
        return tuple(located)

    def _read_verifications(self, view: ProcessView, payload: dict, documents: dict, answer: ReviewAnswer) -> None:
        allowed = {item.code for item in checklist_for(view.process.category) if item.is_semantic}
        for entry in payload.get("verificacoes", []):
            code = entry.get("codigo")
            if code not in allowed:
                continue
            evidence = self._citations(entry, documents, answer)
            try:
                status = CheckStatus(entry.get("status"))
            except ValueError:
                status = CheckStatus.NAO_VERIFICAVEL
            rationale = str(entry.get("justificativa", ""))
            if status is not CheckStatus.NAO_VERIFICAVEL and not evidence:
                status, rationale = (
                    CheckStatus.NAO_VERIFICAVEL,
                    "Conclusão descartada: citação não confere com o documento.",
                )
            answer.semantic_verdicts[code] = SemanticVerdict(status, rationale, evidence, METHOD)

    def _read_classifications(self, payload: dict, documents: dict, answer: ReviewAnswer) -> None:
        for entry in payload.get("classificacoes", []):
            document = documents.get(entry.get("document_id"))
            try:
                document_type = DocumentType(entry.get("tipo"))
            except ValueError:
                continue
            if document is None or locate_quote(document, str(entry.get("trecho", "")), "") is None:
                answer.rejected_citations += 1
                continue
            answer.type_corrections[document.document.document_id] = document_type

    def _read_fields(self, payload: dict, documents: dict, answer: ReviewAnswer) -> None:
        for entry in payload.get("campos", []):
            document = documents.get(entry.get("document_id"))
            name = str(entry.get("campo", ""))
            evidence = locate_quote(document, str(entry.get("trecho", "")), document.label) if document else None
            value = _parse_field_value(name, entry.get("valor", ""))
            if evidence is None or value is None:
                answer.rejected_citations += 1
                continue
            filled = answer.field_fills.setdefault(document.document.document_id, {})
            filled[name] = ExtractedField(value, evidence, METHOD)
