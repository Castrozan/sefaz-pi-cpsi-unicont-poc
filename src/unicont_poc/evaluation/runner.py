from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

from unicont_poc.analysis.cycle import CycleResult
from unicont_poc.evaluation.metrics import outcome_for, summarize
from unicont_poc.persistence.search_index import SearchCriteria
from unicont_poc.persistence.store import AnalysisStore

BASELINE_MINUTES_PER_PROCESS = 163.5
LATENCY_QUERIES = (
    SearchCriteria(text="nota fiscal limpeza"),
    SearchCriteria(document_type="parecer_juridico"),
    SearchCriteria(document_type="contrato", minimum_amount=100000),
    SearchCriteria(text="ressalva", document_type="atesto"),
)


def load_gold(corpus_directory: Path) -> dict[str, dict]:
    lines = (corpus_directory / "gabarito.jsonl").read_text(encoding="utf-8").splitlines()
    return {record["process_number"]: record for record in map(json.loads, lines)}


def measure_search_latency(store: AnalysisStore, repetitions: int = 20) -> dict:
    durations = []
    for _ in range(repetitions):
        for criteria in LATENCY_QUERIES:
            started = time.perf_counter()
            store.search_index.search(criteria)
            durations.append(time.perf_counter() - started)
    return {
        "consultas": len(durations),
        "mediana_ms": round(statistics.median(durations) * 1000, 2),
        "maximo_ms": round(max(durations) * 1000, 2),
    }


def evaluate(corpus_directory: Path, cycle: CycleResult, store: AnalysisStore | None) -> dict:
    gold = load_gold(corpus_directory)
    outcomes = [outcome_for(gold[analysis["process_number"]], analysis) for analysis in cycle.analyses]
    count = len(cycle.analyses)
    per_process = [sum(analysis["timings"].values()) for analysis in cycle.analyses]
    report = summarize(outcomes)
    report["tempo"] = {
        "parede_do_ciclo_segundos": round(cycle.wall_seconds, 1),
        "parede_por_processo_segundos": round(cycle.wall_seconds / count, 3),
        "mediana_por_processo_segundos": round(statistics.median(per_process), 3),
        "p95_por_processo_segundos": round(statistics.quantiles(per_process, n=20)[18], 3),
        "linha_de_base_manual_minutos": BASELINE_MINUTES_PER_PROCESS,
    }
    report["registro_auditavel"] = {
        "analises": count,
        "com_documentos_criterios_resultado_modelo": sum(
            bool(
                a["documents"]
                and a["criteria"]["applied"]
                and a["checks"]
                and a["verdict"]
                and a["model"]["identifier"]
            )
            for a in cycle.analyses
        ),
    }
    report["citacoes_rejeitadas_pela_verificacao"] = sum(a["model"]["rejected_citations"] for a in cycle.analyses)
    report["modelo"] = sorted({f"{a['model']['identifier']} ({a['model']['execution_mode']})" for a in cycle.analyses})
    if store:
        report["busca"] = measure_search_latency(store)
        report["registro_auditavel"]["cadeia_integra"], report["registro_auditavel"]["entradas_na_cadeia"] = (
            store.ledger.verify_chain()
        )
    return report
