from __future__ import annotations

import json
from pathlib import Path

from unicont_poc.evaluation.markdown_report import render_report
from unicont_poc.evaluation.report_text import FAMILY_NOTE, LIMITATIONS, PREAMBLE

WORKERS = 6


def language_seconds_per_request(batch_timings_path: Path) -> float:
    batches = json.loads(batch_timings_path.read_text(encoding="utf-8"))
    return sum(batch["duracao_ms"] for batch in batches) / 1000 / sum(batch["pedidos"] for batch in batches)


def write_report(model_report_path: Path, rules_report_path: Path, batch_timings_path: Path, output_path: Path) -> None:
    model_report = json.loads(model_report_path.read_text(encoding="utf-8"))
    rules_report = json.loads(rules_report_path.read_text(encoding="utf-8"))
    language_seconds = language_seconds_per_request(batch_timings_path)
    serial_seconds = model_report["tempo"]["mediana_por_processo_segundos"] + language_seconds
    context = {
        "preamble": PREAMBLE,
        "family_note": FAMILY_NOTE,
        "limitations": LIMITATIONS,
        "workers": WORKERS,
        "language_seconds_per_request": language_seconds,
        "total_minutes_per_process": serial_seconds / 60,
    }
    output_path.write_text(render_report(model_report, rules_report, context), encoding="utf-8")
