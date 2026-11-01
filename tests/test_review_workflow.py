import pytest

from unicont_poc.adapters.sincin_outbox import NotApprovedByAnalyst, SincinOutboxStub
from unicont_poc.analysis.review_workflow import AnalystReview, ReviewRejected
from unicont_poc.persistence.search_index import SearchCriteria
from unicont_poc.persistence.store import AnalysisStore

NUMBER = "90001.000001/2026-11"


def analysis() -> dict:
    return {
        "analysis_id": "a-1",
        "process_number": NUMBER,
        "category": "pagamento",
        "nucleus_code": "NCI-01",
        "risk": {"level": "alto", "priority_score": 9.0, "reasons": []},
        "verdict": "nao_conforme",
        "opinion_draft": "Minuta.",
        "documents": [],
        "checks": [{"code": "PAG-01", "status": "nao_conforme"}],
    }


@pytest.fixture
def store(tmp_path):
    store = AnalysisStore(tmp_path / "estado.sqlite")
    store.save_analysis(analysis(), {})
    return store


def test_outbox_refuses_analysis_no_analyst_approved(store):
    with pytest.raises(NotApprovedByAnalyst):
        SincinOutboxStub(store).publish_approved_opinion({"process_number": NUMBER})


def test_approval_publishes_and_is_recorded(store):
    review = AnalystReview(store, SincinOutboxStub(store))
    protocol = review.decide(NUMBER, "Analista Teste", True, "Minuta editada.")
    assert protocol.startswith("STUB-")
    decision = store.ledger.entries_for(NUMBER)[-1]
    assert decision["event_type"] == "decisao_do_analista"
    assert decision["payload"]["edited_opinion"] is True


def test_return_requires_justification_and_sends_nothing(store):
    review = AnalystReview(store, SincinOutboxStub(store))
    with pytest.raises(ReviewRejected):
        review.decide(NUMBER, "Analista Teste", False, "Minuta.")
    assert review.decide(NUMBER, "Analista Teste", False, "Minuta.", "Falta documento") is None
    assert store.connection.execute("SELECT count(*) FROM sincin_outbox").fetchone()[0] == 0


def test_decision_requires_analyst_and_happens_once(store):
    review = AnalystReview(store, SincinOutboxStub(store))
    with pytest.raises(ReviewRejected):
        review.decide(NUMBER, "  ", True, "Minuta.")
    review.decide(NUMBER, "Analista Teste", True, "Minuta.")
    with pytest.raises(ReviewRejected):
        review.decide(NUMBER, "Analista Teste", True, "Minuta.")


def test_tampering_with_a_ledger_entry_breaks_the_chain(store):
    AnalystReview(store, SincinOutboxStub(store)).decide(NUMBER, "Analista Teste", True, "Minuta.")
    assert store.ledger.verify_chain()[0] is True
    store.connection.execute("UPDATE audit_ledger SET payload = '{}' WHERE sequence = 1")
    assert store.ledger.verify_chain() == (False, 1)


def test_search_index_ignores_accents_and_filters_by_field(tmp_path):
    store = AnalysisStore(tmp_path / "busca.sqlite")
    record = analysis()
    record["documents"] = [
        {
            "document_id": "d-1",
            "document_type": "contrato",
            "label": "Contrato",
            "fields": {"amount": {"value": "1500.00"}, "cnpj": {"value": "11.222.333/0001-81"}},
        }
    ]
    store.save_analysis(record, {"d-1": [(1, "Serviço de manutenção predial")]})
    assert len(store.search_index.search(SearchCriteria(text="manutencao"))) == 1
    assert len(store.search_index.search(SearchCriteria(cnpj="11.222.333/0001-81", minimum_amount=1000))) == 1
    assert store.search_index.search(SearchCriteria(document_type="parecer_juridico")) == []


def test_approval_requires_opinion_text(store):
    review = AnalystReview(store, SincinOutboxStub(store))
    with pytest.raises(ReviewRejected):
        review.decide(NUMBER, "Analista Teste", True, "   ")
    assert store.connection.execute("SELECT count(*) FROM sincin_outbox").fetchone()[0] == 0


def test_rewriting_who_an_entry_belongs_to_breaks_the_chain(store):
    store.connection.execute("UPDATE audit_ledger SET process_number = 'outro' WHERE sequence = 1")
    assert store.ledger.verify_chain() == (False, 1)
