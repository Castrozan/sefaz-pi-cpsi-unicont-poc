from __future__ import annotations

import gzip
import json
import shutil
from pathlib import Path

from jinja2 import Environment

from unicont_poc.domain import DOCUMENT_TYPE_LABELS, DocumentType
from unicont_poc.persistence.store import AnalysisStore
from unicont_poc.web import presentation
from unicont_poc.web.dashboard import build_dashboard, duplicate_alerts
from unicont_poc.web.routes import StaticRoutes, process_slug
from unicont_poc.web.templating import build_template_environment

WEB_DIRECTORY = Path(__file__).parent
SEARCH_DATABASE_NAME = "busca.sqlite"


def _write_page(environment: Environment, output: Path, template: str, screen: str, context: dict) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(environment.get_template(template).render(screen=screen, **context), encoding="utf-8")


def _export_assets(output: Path) -> None:
    shutil.copytree(WEB_DIRECTORY / "static", output / "estatico")
    shutil.copytree(WEB_DIRECTORY / "site_estatico", output / "estatico" / "site")


def _export_search_database(store: AnalysisStore, output: Path) -> None:
    raw_database = output / "estatico" / "site" / SEARCH_DATABASE_NAME
    store.export_search_database(raw_database)
    with raw_database.open("rb") as raw, gzip.open(raw_database.with_suffix(".sqlite.gz"), "wb") as compressed:
        shutil.copyfileobj(raw, compressed)
    raw_database.unlink()


def _export_lists(environment: Environment, store: AnalysisStore, report_path: Path, output: Path) -> None:
    records = store.all_records()
    dashboard = build_dashboard(records)
    rows = store.queue()
    queue_context = {
        "rows": rows,
        "row_count": len(rows),
        "alerts": duplicate_alerts(records)[:6],
        "dashboard": dashboard,
        "nuclei": sorted({record["nucleus_code"] for record in records}),
        "filters": {"nucleo": "", "risco": "", "situacao": ""},
    }
    search_context = {
        "results": [],
        "has_query": False,
        "elapsed": "",
        "types": [(kind.value, DOCUMENT_TYPE_LABELS[kind]) for kind in DocumentType],
        "form": dict.fromkeys(("texto", "tipo", "cnpj", "processo", "minimo", "maximo"), ""),
    }
    report = json.loads(report_path.read_text(encoding="utf-8"))
    _write_page(environment, output / "index.html", "queue.html", "fila", queue_context)
    _write_page(environment, output / "busca" / "index.html", "search.html", "busca", search_context)
    _write_page(environment, output / "painel" / "index.html", "dashboard.html", "painel", {"dashboard": dashboard})
    _write_page(environment, output / "avaliacao" / "index.html", "evaluation.html", "avaliacao", {"report": report})


def _export_processes(environment: Environment, store: AnalysisStore, output: Path) -> int:
    is_intact, entry_count = store.ledger.verify_chain()
    rows = store.queue()
    ledger_head = store.ledger.head_hash()
    for row in rows:
        number = row["process_number"]
        slug = process_slug(number)
        process_context = {
            "analysis": store.analysis(number),
            "error": "",
            "protocol": "",
            "ledger_head": ledger_head,
            "ledger_entry_count": entry_count,
        }
        audit_context = {
            "process_number": number,
            "entries": store.ledger.entries_for(number),
            "is_intact": is_intact,
            "entry_count": entry_count,
            "ledger_head": ledger_head,
        }
        _write_page(environment, output / "processo" / slug / "index.html", "process.html", "processo", process_context)
        _write_page(environment, output / "auditoria" / slug / "index.html", "audit.html", "auditoria", audit_context)
    return len(rows)


def _export_documents(environment: Environment, store: AnalysisStore, output: Path) -> int:
    identifiers = store.document_identifiers()
    for document_id in identifiers:
        document = store.document(document_id)
        pages = [{"number": number, "html": presentation.highlighted_page(body, "")} for number, body in document["pages"]]
        context = {
            "document_id": document_id,
            "label": document["label"],
            "process_number": document["process_number"],
            "pages": pages,
        }
        _write_page(environment, output / "documento" / document_id / "index.html", "document.html", "documento", context)
    return len(identifiers)


def export_site(store: AnalysisStore, report_path: Path, output: Path, base_path: str) -> str:
    output.mkdir(parents=True)
    environment = build_template_environment(StaticRoutes(base_path), static_site=True)
    _export_assets(output)
    _export_search_database(store, output)
    _export_lists(environment, store, report_path, output)
    process_count = _export_processes(environment, store, output)
    document_count = _export_documents(environment, store, output)
    return f"site em {output}: {process_count} processos, {document_count} documentos"
