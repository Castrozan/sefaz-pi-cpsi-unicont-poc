from __future__ import annotations

import json
import time
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from unicont_poc.adapters.sincin_outbox import SincinOutboxStub
from unicont_poc.analysis.review_workflow import AnalystReview, ReviewRejected
from unicont_poc.domain import DOCUMENT_TYPE_LABELS, DocumentType
from unicont_poc.persistence.search_index import SearchCriteria
from unicont_poc.persistence.store import AnalysisStore
from unicont_poc.web import presentation
from unicont_poc.web.dashboard import build_dashboard, duplicate_alerts
from unicont_poc.web.routes import ServerRoutes
from unicont_poc.web.templating import build_template_environment

WEB_DIRECTORY = Path(__file__).parent


def _parse_amount(text: str) -> float | None:
    cleaned = text.strip().replace(".", "").replace(",", ".")
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def create_application(store: AnalysisStore, corpus_directory: Path, report_path: Path) -> FastAPI:
    application = FastAPI(title="UNICONT – assistente de conformidade", docs_url=None, redoc_url=None)
    application.mount("/estatico", StaticFiles(directory=WEB_DIRECTORY / "static"), name="estatico")
    templates = Jinja2Templates(env=build_template_environment(ServerRoutes()))
    review = AnalystReview(store, SincinOutboxStub(store))

    @application.get("/", response_class=HTMLResponse)
    def queue(request: Request, nucleo: str = "", risco: str = "", situacao: str = ""):
        rows = store.queue(nucleo, risco, situacao)
        records = store.all_records()
        context = {
            "rows": rows[:60],
            "row_count": len(rows),
            "alerts": duplicate_alerts(records)[:6],
            "dashboard": build_dashboard(records),
            "nuclei": sorted({record["nucleus_code"] for record in records}),
            "filters": {"nucleo": nucleo, "risco": risco, "situacao": situacao},
        }
        return templates.TemplateResponse(request, "queue.html", context)

    @application.get("/processo", response_class=HTMLResponse)
    def process_detail(request: Request, numero: str, erro: str = "", protocolo: str = ""):
        analysis = store.analysis(numero)
        if analysis is None:
            raise HTTPException(404, "Processo não encontrado")
        return templates.TemplateResponse(
            request, "process.html", {"analysis": analysis, "error": erro, "protocol": protocolo}
        )

    @application.post("/processo/decisao")
    def decide(
        numero: str = Form(),
        analista: str = Form(""),
        decisao: str = Form(),
        parecer: str = Form(""),
        justificativa: str = Form(""),
    ):
        parameters = f"numero={numero}"
        try:
            protocol = review.decide(numero, analista, decisao == "aprovar", parecer, justificativa)
        except ReviewRejected as rejection:
            return RedirectResponse(f"/processo?{parameters}&erro={rejection}", status_code=303)
        suffix = f"&protocolo={protocol}" if protocol else ""
        return RedirectResponse(f"/processo?{parameters}{suffix}", status_code=303)

    @application.get("/documento/{document_id}", response_class=HTMLResponse)
    def document_view(request: Request, document_id: str, trecho: str = "", numero: str = ""):
        document = store.document(document_id)
        if document is None:
            raise HTTPException(404, "Documento não encontrado")
        pages = [
            {"number": number, "html": presentation.highlighted_page(body, trecho)} for number, body in document["pages"]
        ]
        context = {
            "document_id": document_id,
            "label": document["label"],
            "process_number": document["process_number"],
            "pages": pages,
        }
        return templates.TemplateResponse(request, "document.html", context)

    @application.get("/documento/{document_id}/original")
    def document_original(document_id: str):
        path = corpus_directory / "documentos" / document_id.rsplit("-", 1)[0] / f"{document_id}.pdf"
        if not path.exists():
            raise HTTPException(404, "PDF não gerado nesta instalação; execute unicont-poc gerar avaliacao")
        return FileResponse(path, media_type="application/pdf")

    @application.get("/busca", response_class=HTMLResponse)
    def search(
        request: Request,
        texto: str = "",
        tipo: str = "",
        cnpj: str = "",
        processo: str = "",
        minimo: str = "",
        maximo: str = "",
    ):
        has_query = any((texto, tipo, cnpj, processo, minimo, maximo))
        criteria = SearchCriteria(texto, tipo, cnpj, processo, _parse_amount(minimo), _parse_amount(maximo))
        started = time.perf_counter()
        results = store.search_index.search(criteria) if has_query else []
        elapsed_milliseconds = (time.perf_counter() - started) * 1000
        context = {
            "results": results,
            "has_query": has_query,
            "elapsed": f"{elapsed_milliseconds:.1f}".replace(".", ","),
            "types": [(kind.value, DOCUMENT_TYPE_LABELS[kind]) for kind in DocumentType],
            "form": {
                "texto": texto,
                "tipo": tipo,
                "cnpj": cnpj,
                "processo": processo,
                "minimo": minimo,
                "maximo": maximo,
            },
        }
        return templates.TemplateResponse(request, "search.html", context)

    @application.get("/painel", response_class=HTMLResponse)
    def dashboard_view(request: Request):
        return templates.TemplateResponse(
            request, "dashboard.html", {"dashboard": build_dashboard(store.all_records())}
        )

    @application.get("/avaliacao", response_class=HTMLResponse)
    def evaluation_view(request: Request):
        report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else None
        return templates.TemplateResponse(request, "evaluation.html", {"report": report})

    @application.get("/auditoria", response_class=HTMLResponse)
    def audit_view(request: Request, numero: str):
        is_intact, entry_count = store.ledger.verify_chain()
        context = {
            "process_number": numero,
            "entries": store.ledger.entries_for(numero),
            "is_intact": is_intact,
            "entry_count": entry_count,
        }
        return templates.TemplateResponse(request, "audit.html", context)

    return application
