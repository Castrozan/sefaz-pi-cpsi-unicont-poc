import pytest
from fastapi.testclient import TestClient

from unicont_poc.persistence.store import AnalysisStore
from unicont_poc.web.application import create_application

NUMBER = "90001.000001/2026-11"


def record() -> dict:
    return {
        "analysis_id": "a-1",
        "process_number": NUMBER,
        "category": "pagamento",
        "organ_name": "Órgão Sintético 01",
        "nucleus_code": "NCI-01",
        "process_value": "1500.00",
        "summary": "Resumo de teste.",
        "opinion_draft": "Minuta.",
        "verdict": "nao_conforme",
        "risk": {"level": "alto", "priority_score": 9.0, "reasons": ["PAG-05: valor diverge"]},
        "criteria": {"version": "v", "applied": ["PAG-05"]},
        "model": {"identifier": "modelo", "execution_mode": "teste", "pipeline_version": "0.1.0"},
        "documents": [
            {
                "document_id": "d-001",
                "document_type": "nota_fiscal",
                "label": "Nota fiscal",
                "declared_title": "Anexo",
                "method": "regra",
                "was_scanned": False,
                "sha256": "0" * 64,
                "fields": {"amount": {"value": "1500.00"}, "cnpj": {"value": "11.222.333/0001-81"}},
            }
        ],
        "checks": [
            {
                "code": "PAG-05",
                "title": "Valor pago",
                "legal_basis": "Lei",
                "status": "nao_conforme",
                "rationale": "Diverge.",
                "method": "regra",
                "evidence": [
                    {"document_id": "d-001", "page_number": 1, "quote": "R$ 1.500,00", "document_label": "Nota fiscal"}
                ],
            }
        ],
    }


@pytest.fixture
def client(tmp_path):
    store = AnalysisStore(tmp_path / "estado.sqlite")
    store.save_analysis(record(), {"d-001": [(1, "Valor total R$ 1.500,00 <script>alert(1)</script>")]})
    return TestClient(create_application(store, tmp_path, tmp_path / "ausente.json"))


def test_pages_render_in_portuguese(client):
    assert "Fila de análise" in client.get("/").text
    assert "Inconsistências mais frequentes" in client.get("/painel").text
    assert "Relatório ainda não gerado" in client.get("/avaliacao").text
    assert "PAG-05" in client.get("/processo", params={"numero": NUMBER}).text


def test_cited_quote_is_highlighted_and_document_text_is_escaped(client):
    page = client.get("/documento/d-001", params={"trecho": "R$ 1.500,00"}).text
    assert '<mark id="citacao">R$ 1.500,00</mark>' in page
    assert "<script>alert" not in page


def test_search_by_type_and_keyword(client):
    assert NUMBER in client.get("/busca", params={"tipo": "nota_fiscal"}).text
    assert "<mark>" in client.get("/busca", params={"texto": "valor"}).text


def test_analyst_decision_round_trip(client):
    response = client.post(
        "/processo/decisao",
        data={"numero": NUMBER, "analista": "Analista", "decisao": "aprovar", "parecer": "Minuta."},
        follow_redirects=True,
    )
    assert "Protocolo STUB-" in response.text
    assert "Decisão do analista" in client.get("/auditoria", params={"numero": NUMBER}).text


def test_decision_without_analyst_shows_error(client):
    response = client.post(
        "/processo/decisao", data={"numero": NUMBER, "decisao": "aprovar", "parecer": "Minuta."}, follow_redirects=True
    )
    assert "identificação do analista" in response.text


def test_unknown_process_is_404(client):
    assert client.get("/processo", params={"numero": "x"}).status_code == 404
