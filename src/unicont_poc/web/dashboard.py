from __future__ import annotations

from collections import Counter, defaultdict

from unicont_poc.corpus.catalog import CHECKLIST_BY_CODE


def duplicate_alerts(records: list[dict]) -> list[dict]:
    alerts = []
    for record in records:
        for check in record["checks"]:
            if check["code"] == "PAG-09" and check["status"] == "nao_conforme":
                alerts.append({"process_number": record["process_number"], "rationale": check["rationale"]})
    return alerts


def build_dashboard(records: list[dict]) -> dict:
    by_nucleus: dict[str, Counter] = defaultdict(Counter)
    inconsistencies: Counter = Counter()
    pending_reasons: Counter = Counter()
    for record in records:
        counters = by_nucleus[record["nucleus_code"]]
        counters["processos"] += 1
        counters[f"risco_{record['risk']['level']}"] += 1
        counters[record["review_state"]] += 1
        for check in record["checks"]:
            if check["status"] == "nao_conforme":
                inconsistencies[check["code"]] += 1
                counters["apontamentos"] += 1
            if check["status"] == "nao_verificavel":
                pending_reasons[check["code"]] += 1
    nuclei = [{"nucleus_code": code, **counters} for code, counters in by_nucleus.items()]
    nuclei.sort(key=lambda entry: (entry.get("risco_alto", 0), entry["processos"]), reverse=True)
    top = inconsistencies.most_common(10)
    maximum = top[0][1] if top else 1
    return {
        "total": len(records),
        "category_counts": Counter(record["category"] for record in records),
        "risk_counts": Counter(record["risk"]["level"] for record in records),
        "review_counts": Counter(record["review_state"] for record in records),
        "nuclei": nuclei[:15],
        "nucleus_count": len(nuclei),
        "top_inconsistencies": [
            {"code": code, "title": CHECKLIST_BY_CODE[code].title, "count": count, "share": count / maximum}
            for code, count in top
        ],
        "pending_reasons": [
            {"code": code, "title": CHECKLIST_BY_CODE[code].title, "count": count}
            for code, count in pending_reasons.most_common(5)
        ],
    }
