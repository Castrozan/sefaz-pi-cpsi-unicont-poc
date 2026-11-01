from __future__ import annotations

import time
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from unicont_poc.adapters.synthetic_sei import SyntheticSeiGateway
from unicont_poc.analysis.pipeline import PreparedProcess, classify_process, conclude_process, prepare_process
from unicont_poc.analysis.process_view import ProcessView
from unicont_poc.analysis.review.review_contract import ReviewStage
from unicont_poc.domain import DocumentType
from unicont_poc.persistence.store import AnalysisStore


def _read_and_classify(arguments: tuple[Path, str]) -> tuple[ProcessView, float]:
    corpus_directory, process_number = arguments
    started = time.perf_counter()
    view = classify_process(SyntheticSeiGateway(corpus_directory).fetch_process(process_number))
    return view, time.perf_counter() - started


def read_cycle(corpus_directory: Path, workers: int) -> list[tuple[ProcessView, float]]:
    process_numbers = SyntheticSeiGateway(corpus_directory).process_numbers()
    arguments = [(corpus_directory, number) for number in process_numbers]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(_read_and_classify, arguments, chunksize=4))


def mark_duplicate_invoices(prepared_processes: list[PreparedProcess]) -> None:
    first_seen: dict[tuple[object, object], str] = {}
    for prepared in sorted(prepared_processes, key=lambda item: item.view.process.process_number[6:]):
        for invoice in prepared.view.of_type(DocumentType.NOTA_FISCAL):
            key = (invoice.value("cnpj"), invoice.value("invoice_number"))
            if None in key:
                continue
            if key in first_seen and first_seen[key] != prepared.view.process.process_number:
                prepared.view.duplicate_of[invoice.document.document_id] = first_seen[key]
            first_seen.setdefault(key, prepared.view.process.process_number)


@dataclass(frozen=True)
class CycleResult:
    analyses: list[dict]
    wall_seconds: float
    read_seconds: float


def run_cycle(
    corpus_directory: Path,
    review: ReviewStage,
    store: AnalysisStore | None,
    workers: int = 6,
    progress: Callable[[int, int], None] | None = None,
) -> CycleResult:
    started = time.perf_counter()
    read_results = read_cycle(corpus_directory, workers)
    read_seconds = time.perf_counter() - started
    prepared_processes = []
    for position, (view, reading_seconds) in enumerate(read_results, start=1):
        prepared = prepare_process(view, review)
        prepared.timings["leitura_classificacao_segundos"] = reading_seconds
        prepared_processes.append(prepared)
        if progress:
            progress(position, len(read_results))
    mark_duplicate_invoices(prepared_processes)
    analyses = [conclude_process(prepared) for prepared in prepared_processes]
    if store:
        for prepared, analysis in zip(prepared_processes, analyses):
            pages = {
                document.document_id: [(page.page_number, page.canonical_text) for page in document.pages]
                for document in prepared.view.process.documents
            }
            store.save_analysis(analysis, pages)
    return CycleResult(analyses, time.perf_counter() - started, read_seconds)
