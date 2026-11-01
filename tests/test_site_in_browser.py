import gzip
import http.server
import json
import os
import shutil
import threading
from functools import partial
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect, sync_playwright

from unicont_poc.persistence.search_index import SearchCriteria
from unicont_poc.persistence.store import AnalysisStore
from unicont_poc.web.presentation import money_label, percent_label
from unicont_poc.web.static_export import export_site

BASE = "/sefaz-pi-cpsi-unicont-poc"
DATA = Path("dados")
REPORT = json.loads((DATA / "avaliacao.json").read_text(encoding="utf-8"))
HOSTILE_TEXT = '<img src=x onerror="window.hostileRan=true">'
SEARCHES = [
    ({"texto": "ressalva"}, SearchCriteria(text="ressalva")),
    ({"texto": "certidao"}, SearchCriteria(text="certidao")),
    ({"tipo": "nota_fiscal", "minimo": "1.000,00", "maximo": "5.000,00"},
     SearchCriteria(document_type="nota_fiscal", minimum_amount=1000.0, maximum_amount=5000.0)),
]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *arguments):
        pass


@pytest.fixture(scope="session")
def source_store(tmp_path_factory):
    database = tmp_path_factory.mktemp("estado") / "estado.sqlite"
    with gzip.open(DATA / "estado-demo.sqlite.gz", "rb") as snapshot, database.open("wb") as restored:
        shutil.copyfileobj(snapshot, restored)
    return AnalysisStore(database)


@pytest.fixture(scope="session")
def site_url(tmp_path_factory, source_store):
    if os.environ.get("UNICONT_SITE_URL"):
        yield os.environ["UNICONT_SITE_URL"].rstrip("/")
        return
    root = tmp_path_factory.mktemp("publicado")
    export_site(source_store, DATA / "avaliacao.json", root / BASE.strip("/"), BASE)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}{BASE}"
    server.shutdown()


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as playwright:
        chromium = playwright.chromium.launch()
        yield chromium
        chromium.close()


@pytest.fixture
def page(browser):
    context = browser.new_context()
    opened = context.new_page()
    failures = []
    opened.on("pageerror", lambda error: failures.append(str(error)))
    opened.on("console", lambda message: failures.append(message.text) if message.type == "error" else None)
    yield opened
    context.close()
    assert failures == []


@pytest.fixture(scope="session")
def process_number(source_store):
    return source_store.queue()[0]["process_number"]


def process_url(site_url: str, number: str) -> str:
    return f"{site_url}/processo/{number.replace('/', '-')}/"


def open_process(page: Page, site_url: str, number: str) -> None:
    page.goto(process_url(site_url, number))
    page.wait_for_load_state("networkidle")


def approve(page: Page, analyst: str) -> None:
    page.fill("input[name=analista]", analyst)
    page.click("button[value=aprovar]")


@pytest.mark.parametrize("path", ["/", "/busca/", "/painel/", "/avaliacao/"])
def test_screen_shows_the_synthetic_data_banner(page, site_url, path):
    page.goto(site_url + path)
    expect(page.locator(".faixa-sintetica")).to_contain_text("Dados sintéticos.")
    page.click(".faixa-sintetica summary")
    expect(page.locator(".faixa-sintetica")).to_contain_text("SEI e SINCIN+: simulados")


def test_queue_lists_the_cycle_and_filters_on_the_client(page, site_url, source_store):
    page.goto(site_url + "/")
    expect(page.locator("tr[data-processo]:visible")).to_have_count(500)
    high_risk = len(source_store.queue(risk_level="alto"))
    page.select_option("select[name=risco]", "alto")
    page.click("form.filtros button")
    expect(page.locator("tr[data-processo]:visible")).to_have_count(high_risk)
    expect(page.locator("form.filtros .contagem")).to_have_text(f"{high_risk} processo(s)")
    expect(page.locator("select[name=risco]")).to_have_value("alto")


@pytest.mark.parametrize(("parameters", "criteria"), SEARCHES)
def test_browser_search_matches_the_server_search(page, site_url, source_store, parameters, criteria):
    expected = source_store.search_index.search(criteria)
    assert expected
    page.goto(site_url + "/busca/")
    for name, value in parameters.items():
        locator = page.locator(f"[name={name}]")
        locator.select_option(value) if name == "tipo" else locator.fill(value)
    page.click("form.busca button")
    rows = page.locator("#resultados-da-busca tbody tr")
    expect(rows).to_have_count(len(expected))
    for index, result in enumerate(expected):
        cells = rows.nth(index).locator("td")
        assert cells.nth(0).inner_text() == result["process_number"]
        assert cells.nth(1).inner_text() == result["document_id"][-3:]
        assert cells.nth(3).inner_text() == money_label(result["amount"])
        visible_snippet = (result["snippet"] or "").replace("[[", "").replace("]]", "")
        assert cells.nth(5).text_content() == visible_snippet


def test_search_with_only_punctuation_reports_instead_of_breaking(browser, site_url):
    context = browser.new_context()
    page = context.new_page()
    page.goto(f"{site_url}/busca/?texto=%21%21")
    expect(page.locator("#situacao-da-busca")).to_contain_text("Não foi possível executar a busca")
    context.close()


def test_dashboard_and_evaluation_show_the_measured_numbers(page, site_url):
    page.goto(site_url + "/painel/")
    expect(page.locator(".numeros")).to_contain_text("500")
    page.goto(site_url + "/avaliacao/")
    summary = REPORT["global"]
    for value in (
        summary["taxa_de_acerto_processo"],
        summary["acerto_exato_do_conjunto"],
        summary["linha_de_base_sempre_conforme"],
    ):
        expect(page.locator(".numeros")).to_contain_text(percent_label(value))
    assert percent_label(summary["taxa_de_acerto_processo"]) == "94,0%"
    prestacao = REPORT["por_categoria"]["prestacao_de_contas"]["taxa_de_acerto_processo"]
    expect(page.locator("table").first).to_contain_text(percent_label(prestacao))


def test_citation_opens_the_document_with_the_quote_highlighted(page, site_url, process_number):
    open_process(page, site_url, process_number)
    citation = page.locator("a.citacao").first
    citation.click()
    expect(page.locator("mark#citacao")).to_be_visible()


def test_hostile_quote_in_the_url_stays_text(page, site_url, source_store, process_number):
    document_id = source_store.analysis(process_number)["documents"][0]["document_id"]
    page.goto(f"{site_url}/documento/{document_id}/?trecho=<img src=x onerror=window.hostileRan=true>")
    page.wait_for_load_state("networkidle")
    assert page.evaluate("window.hostileRan") is None


def test_decision_refusals_match_the_server_rules(page, site_url, process_number):
    open_process(page, site_url, process_number)
    failure = page.locator("#erro-da-decisao")
    page.click("button[value=aprovar]")
    expect(failure).to_have_text("A decisão exige a identificação do analista.")
    page.fill("input[name=analista]", "Analista de Teste")
    page.fill("textarea[name=parecer]", "   ")
    page.click("button[value=aprovar]")
    expect(failure).to_have_text("A aprovação exige o texto do parecer.")
    page.click("button[value=devolver]")
    expect(failure).to_have_text("A devolução exige justificativa.")
    expect(page.locator("#formulario-de-decisao")).to_be_visible()


def test_approval_flows_through_queue_dashboard_and_audit_then_clears(page, site_url, source_store, process_number):
    open_process(page, site_url, process_number)
    approve(page, "Analista de Teste")
    expect(page.locator("#sucesso-da-decisao")).to_contain_text("Protocolo SIMULADO-")
    expect(page.locator("#formulario-de-decisao")).to_be_hidden()

    page.reload()
    expect(page.locator("#decisao-registrada")).to_contain_text("Analista de Teste")
    expect(page.locator("#formulario-de-decisao")).to_be_hidden()

    page.goto(f"{site_url}/?situacao=aprovado")
    expect(page.locator("tr[data-processo]:visible")).to_have_count(1)
    expect(page.locator("[data-contador-aguardando]")).to_have_text("499")

    nucleus = source_store.analysis(process_number)["nucleus_code"]
    page.goto(site_url + "/painel/")
    aguardando = page.locator(f'[data-aguardando-nucleo="{nucleus}"]')
    if aguardando.count():
        expected = len(source_store.queue(nucleus_code=nucleus)) - 1
        expect(aguardando).to_have_text(str(expected))

    page.goto(f"{site_url}/auditoria/{process_number.replace('/', '-')}/")
    local_entry = page.locator("#registro-local")
    expect(local_entry).to_contain_text("#501 Decisão do analista, simulada neste navegador")
    expect(local_entry).to_contain_text("Íntegra")

    page.click("#limpar-decisoes")
    page.wait_for_load_state("networkidle")
    open_process(page, site_url, process_number)
    expect(page.locator("#formulario-de-decisao")).to_be_visible()


def test_returning_requires_a_note_and_sends_no_protocol(page, site_url, process_number):
    open_process(page, site_url, process_number)
    page.fill("input[name=analista]", "Analista de Teste")
    page.fill("input[name=justificativa]", "Falta certidão")
    page.click("button[value=devolver]")
    expect(page.locator("#decisao-registrada")).to_contain_text("Devolvido pelo analista")
    expect(page.locator("#decisao-registrada")).not_to_contain_text("Protocolo")
    expect(page.locator("#sucesso-da-decisao")).to_be_hidden()


def test_hostile_analyst_name_stays_text(page, site_url, process_number):
    open_process(page, site_url, process_number)
    approve(page, HOSTILE_TEXT)
    expect(page.locator("#decisao-registrada")).to_contain_text(HOSTILE_TEXT)
    page.goto(f"{site_url}/auditoria/{process_number.replace('/', '-')}/")
    expect(page.locator("#registro-local")).to_contain_text(HOSTILE_TEXT)
    assert page.evaluate("window.hostileRan") is None


def test_tampered_local_decision_is_reported_as_broken_chain(page, site_url, process_number):
    open_process(page, site_url, process_number)
    approve(page, "Analista de Teste")
    expect(page.locator("#decisao-registrada")).to_be_visible()
    page.evaluate(
        """() => {
            const key = "unicont-poc.decisoes.v1";
            const decisions = JSON.parse(localStorage.getItem(key));
            decisions[0].payload.analyst_name = "Outra pessoa";
            localStorage.setItem(key, JSON.stringify(decisions));
        }"""
    )
    page.goto(f"{site_url}/auditoria/{process_number.replace('/', '-')}/")
    expect(page.locator("#registro-local")).to_contain_text("VIOLADA")
