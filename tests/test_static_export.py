import gzip
import json
import re
import sqlite3

import pytest

from test_web import NUMBER, record
from unicont_poc.persistence.search_index import SearchCriteria, SearchIndex
from unicont_poc.persistence.store import AnalysisStore
from unicont_poc.web.static_export import export_site

BASE = "/sefaz-pi-cpsi-unicont-poc"
SLUG = "90001.000001-2026-11"
REPORT = {
    "global": {
        "processos": 1,
        "taxa_de_acerto_processo": 0.94,
        "acerto_exato_do_conjunto": 0.95,
        "linha_de_base_sempre_conforme": 0.534,
    },
    "por_categoria": {},
    "por_familia_de_template": {},
    "por_criterio": [],
}


@pytest.fixture
def store(tmp_path):
    analysis_store = AnalysisStore(tmp_path / "estado.sqlite")
    analysis_store.save_analysis(record(), {"d-001": [(1, "Valor total R$ 1.500,00 <script>alert(1)</script>")]})
    return analysis_store


@pytest.fixture
def report_path(tmp_path):
    path = tmp_path / "avaliacao.json"
    path.write_text(json.dumps(REPORT), encoding="utf-8")
    return path


@pytest.fixture
def site(tmp_path, store, report_path):
    output = tmp_path / "site"
    export_site(store, report_path, output, BASE)
    return output


def exported_pages(site):
    return sorted(site.rglob("index.html"))


def test_every_screen_is_exported(site):
    relative = {str(path.relative_to(site)) for path in exported_pages(site)}
    assert relative == {
        "index.html",
        "busca/index.html",
        "painel/index.html",
        "avaliacao/index.html",
        f"processo/{SLUG}/index.html",
        f"auditoria/{SLUG}/index.html",
        "documento/d-001/index.html",
    }


def test_every_page_states_synthetic_data_and_what_is_simulated(site):
    for page in exported_pages(site):
        text = page.read_text(encoding="utf-8")
        assert "Dados sintéticos." in text
        assert "O que é simulado neste site" in text


def test_every_internal_link_stays_under_the_base_path(site):
    for page in exported_pages(site):
        for target in re.findall(r'(?:href|src)="([^"]+)"', page.read_text(encoding="utf-8")):
            assert target.startswith((BASE, "https://")), f"{page}: {target}"


def test_every_internal_link_resolves_to_an_exported_file(site):
    for page in exported_pages(site):
        for target in re.findall(rf'(?:href|src)="{BASE}/([^"?#]*)', page.read_text(encoding="utf-8")):
            resolved = site / target
            assert (resolved / "index.html").exists() or resolved.is_file(), f"{page}: {target}"


def test_document_text_is_escaped(site):
    assert "<script>alert" not in (site / "documento/d-001/index.html").read_text(encoding="utf-8")


def test_evaluation_shows_the_report_numbers(site):
    text = (site / "avaliacao/index.html").read_text(encoding="utf-8")
    assert "94,0%" in text and "53,4%" in text


def test_decision_form_never_posts_to_a_server(site):
    text = (site / f"processo/{SLUG}/index.html").read_text(encoding="utf-8")
    assert 'action=""' in text and "/processo/decisao" not in text


def test_search_database_answers_like_the_source_and_holds_only_the_index(tmp_path, site, store):
    extracted = tmp_path / "busca.sqlite"
    extracted.write_bytes(gzip.decompress((site / "estatico/site/busca.sqlite.gz").read_bytes()))
    connection = sqlite3.connect(extracted)
    tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert not tables & {"analyses", "audit_ledger", "sincin_outbox"}
    criteria = SearchCriteria(text="valor")
    assert SearchIndex(connection).search(criteria) == store.search_index.search(criteria)


def test_existing_output_is_refused(tmp_path, store, report_path):
    (tmp_path / "ocupado").mkdir()
    with pytest.raises(FileExistsError):
        export_site(store, report_path, tmp_path / "ocupado", BASE)


def test_source_state_is_not_changed(tmp_path, site, store):
    assert store.queue()[0]["process_number"] == NUMBER
    assert store.ledger.verify_chain() == (True, 1)
