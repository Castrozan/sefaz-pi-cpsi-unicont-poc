from __future__ import annotations

import json
from pathlib import Path

from unicont_poc.evaluation.markdown_report import render_report
from unicont_poc.evaluation.report_text import FAMILY_NOTE, LIMITATIONS, PREAMBLE

LANGUAGE_SECONDS_PER_REQUEST = 4835.284 / 500
WORKERS = 6


def write_report(model_report_path: Path, rules_report_path: Path, output_path: Path) -> None:
    model_report = json.loads(model_report_path.read_text(encoding="utf-8"))
    rules_report = json.loads(rules_report_path.read_text(encoding="utf-8"))
    serial_seconds = model_report["tempo"]["mediana_por_processo_segundos"] + LANGUAGE_SECONDS_PER_REQUEST
    context = {
        "preamble": PREAMBLE,
        "family_note": FAMILY_NOTE,
        "limitations": LIMITATIONS,
        "workers": WORKERS,
        "language_seconds_per_request": LANGUAGE_SECONDS_PER_REQUEST,
        "total_minutes_per_process": serial_seconds / 60,
    }
    output_path.write_text(render_report(model_report, rules_report, context), encoding="utf-8")
