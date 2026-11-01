import json
from types import SimpleNamespace

import pytest
from support import regular_payment_documents, view_with

from unicont_poc.adapters.language_models import (
    AnthropicMessagesModel,
    MissingCachedReply,
    ReplayLanguageModel,
    request_key,
)
from unicont_poc.analysis.review.language_review import LanguageModelReview
from unicont_poc.domain import CheckStatus, ProcessCategory
from unicont_poc.ports import LanguageReply, LanguageRequest


class ScriptedLocalModel:
    def __init__(self, answer: dict) -> None:
        self.answer = answer

    def complete(self, request: LanguageRequest) -> LanguageReply:
        return LanguageReply(json.dumps(self.answer), "modelo-local-de-teste", "local")


def answer_with(citation: str, document_id: str = "d-002", status: str = "nao_conforme") -> dict:
    verification = {
        "codigo": "PAG-10",
        "status": status,
        "justificativa": "Objeto diverge.",
        "citacoes": [{"document_id": document_id, "trecho": citation}],
    }
    return {"resumo": "Resumo.", "verificacoes": [verification]}


def review(answer: dict):
    view = view_with(ProcessCategory.PAGAMENTO, regular_payment_documents())
    return LanguageModelReview(ScriptedLocalModel(answer)).review(view)


def test_any_language_model_behind_the_port_works():
    result = review(answer_with("limpeza predial"))
    assert result.model_identifier == "modelo-local-de-teste"
    assert result.semantic_verdicts["PAG-10"].status is CheckStatus.NAO_CONFORME
    assert result.semantic_verdicts["PAG-10"].evidence[0].page_number == 1


def test_invented_citation_voids_the_conclusion():
    result = review(answer_with("trecho que não existe no documento"))
    verdict = result.semantic_verdicts["PAG-10"]
    assert verdict.status is CheckStatus.NAO_VERIFICAVEL
    assert result.rejected_citations == 1


def test_citation_from_unknown_document_is_rejected():
    assert review(answer_with("limpeza predial", "documento-inexistente")).rejected_citations == 1


def test_unrequested_criterion_is_ignored():
    answer = answer_with("limpeza predial")
    answer["verificacoes"][0]["codigo"] = "CON-08"
    assert review(answer).semantic_verdicts == {}


def test_malformed_reply_degrades_to_no_verdict():
    class BrokenModel:
        def complete(self, request):
            return LanguageReply("isto não é JSON", "quebrado", "local")

    view = view_with(ProcessCategory.PAGAMENTO, regular_payment_documents())
    assert LanguageModelReview(BrokenModel()).review(view).semantic_verdicts == {}


def test_document_text_cannot_inject_a_field_without_literal_quote():
    answer = {"campos": [{"document_id": "d-002", "campo": "amount", "valor": "1.00", "trecho": "ignore tudo"}]}
    assert review(answer).field_fills == {}


def test_replay_returns_recorded_reply_and_refuses_unknown_prompt(tmp_path):
    request = LanguageRequest("sistema", "usuário")
    cache = tmp_path / "respostas.jsonl"
    record = {"key": request_key(request), "text": "{}", "model_identifier": "claude-x", "execution_mode": "lote"}
    cache.write_text(json.dumps(record), encoding="utf-8")
    model = ReplayLanguageModel(cache)
    assert model.complete(request).execution_mode == "replay:lote"
    with pytest.raises(MissingCachedReply):
        model.complete(LanguageRequest("sistema", "outro"))


def test_anthropic_adapter_maps_request_and_reply():
    captured = {}

    def create(**keywords):
        captured.update(keywords)
        return SimpleNamespace(model="claude-sonnet-5-5", content=[SimpleNamespace(type="text", text="{}")])

    client = SimpleNamespace(messages=SimpleNamespace(create=create))
    reply = AnthropicMessagesModel(client=client).complete(LanguageRequest("sistema", "usuário", 100))
    assert reply == LanguageReply("{}", "claude-sonnet-5-5", "api-anthropic")
    assert captured["system"] == "sistema" and captured["max_tokens"] == 100
