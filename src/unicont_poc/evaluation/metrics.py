from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from unicont_poc.corpus.catalog import CHECKLIST
from unicont_poc.domain import ProcessCategory

REAL_MIX = {
    ProcessCategory.PAGAMENTO.value: 5937 / 6735,
    ProcessCategory.CONTRATACAO.value: 421 / 6735,
    ProcessCategory.PRESTACAO_DE_CONTAS.value: 377 / 6735,
}
SEMANTIC_CODES = {item.code for item in CHECKLIST if item.is_semantic}


@dataclass(frozen=True)
class Outcome:
    gold: dict
    analysis: dict
    flagged_codes: frozenset[str]
    unverified_codes: frozenset[str]

    @property
    def expected_codes(self) -> frozenset[str]:
        return frozenset(self.gold["irregularities"])

    @property
    def predicted_irregular(self) -> bool:
        return bool(self.flagged_codes or self.unverified_codes)

    @property
    def verdict_is_correct(self) -> bool:
        return self.predicted_irregular == bool(self.expected_codes)

    @property
    def set_is_exact(self) -> bool:
        return self.flagged_codes == self.expected_codes


def outcome_for(gold: dict, analysis: dict) -> Outcome:
    flagged = frozenset(check["code"] for check in analysis["checks"] if check["status"] == "nao_conforme")
    unverified = frozenset(check["code"] for check in analysis["checks"] if check["status"] == "nao_verificavel")
    return Outcome(gold, analysis, flagged, unverified)


def _rate(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 4) if denominator else None


def _group_summary(outcomes: list[Outcome]) -> dict:
    total = len(outcomes)
    irregular = [outcome for outcome in outcomes if outcome.expected_codes]
    clean = [outcome for outcome in outcomes if not outcome.expected_codes]
    return {
        "processos": total,
        "taxa_de_acerto_processo": _rate(sum(outcome.verdict_is_correct for outcome in outcomes), total),
        "acerto_exato_do_conjunto": _rate(sum(outcome.set_is_exact for outcome in outcomes), total),
        "linha_de_base_sempre_conforme": _rate(len(clean), total),
        "deteccao_em_irregulares": _rate(sum(outcome.predicted_irregular for outcome in irregular), len(irregular)),
        "falso_alarme_em_regulares": _rate(sum(outcome.predicted_irregular for outcome in clean), len(clean)),
        "com_item_nao_verificavel": _rate(sum(bool(outcome.unverified_codes) for outcome in outcomes), total),
    }


def per_check_scores(outcomes: list[Outcome]) -> list[dict]:
    rows = []
    for item in CHECKLIST:
        relevant = [outcome for outcome in outcomes if outcome.gold["category"] == item.category.value]
        true_positive = sum(item.code in o.expected_codes and item.code in o.flagged_codes for o in relevant)
        false_positive = sum(item.code not in o.expected_codes and item.code in o.flagged_codes for o in relevant)
        false_negative = sum(item.code in o.expected_codes and item.code not in o.flagged_codes for o in relevant)
        unverified = sum(item.code in o.unverified_codes for o in relevant)
        rows.append(
            {
                "codigo": item.code,
                "criterio": item.title,
                "semantico": item.is_semantic,
                "casos_semeados": true_positive + false_negative,
                "verdadeiros_positivos": true_positive,
                "falsos_positivos": false_positive,
                "falsos_negativos": false_negative,
                "nao_verificaveis": unverified,
                "precisao": _rate(true_positive, true_positive + false_positive),
                "revocacao": _rate(true_positive, true_positive + false_negative),
            }
        )
    return rows


def _amounts_equal(expected: str, found: object) -> bool:
    try:
        return found is not None and Decimal(str(found)) == Decimal(expected)
    except InvalidOperation:
        return False


def document_scores(outcomes: list[Outcome]) -> dict:
    type_hits, type_totals, scan_hits, scan_totals = Counter(), Counter(), Counter(), Counter()
    field_hits, field_totals = Counter(), Counter()
    confusions: Counter = Counter()
    for outcome in outcomes:
        found = {document["document_id"]: document for document in outcome.analysis["documents"]}
        for document_id, gold_document in outcome.gold["documents"].items():
            document = found[document_id]
            expected_type = gold_document["document_type"]
            is_hit = document["document_type"] == expected_type
            type_totals[expected_type] += 1
            type_hits[expected_type] += is_hit
            scan_key = "digitalizado" if gold_document["was_scanned"] else "texto_nativo"
            scan_totals[scan_key] += 1
            scan_hits[scan_key] += is_hit
            if not is_hit:
                confusions[(expected_type, document["document_type"])] += 1
            for name, expected in gold_document["fields"].items():
                value = document["fields"].get(name, {}).get("value")
                field_totals[name] += 1
                field_hits[name] += _amounts_equal(expected, value) if name == "amount" else value == expected
    return {
        "classificacao_global": _rate(sum(type_hits.values()), sum(type_totals.values())),
        "classificacao_por_tipo": {kind: _rate(type_hits[kind], type_totals[kind]) for kind in sorted(type_totals)},
        "documentos_por_tipo": dict(sorted(type_totals.items())),
        "classificacao_por_origem": {kind: _rate(scan_hits[kind], scan_totals[kind]) for kind in sorted(scan_totals)},
        "documentos_por_origem": dict(sorted(scan_totals.items())),
        "extracao_por_campo": {name: _rate(field_hits[name], field_totals[name]) for name in sorted(field_totals)},
        "campos_avaliados": dict(sorted(field_totals.items())),
        "confusoes_mais_frequentes": [
            {"esperado": expected, "obtido": obtained, "casos": count}
            for (expected, obtained), count in confusions.most_common(8)
        ],
    }


def summarize(outcomes: list[Outcome]) -> dict:
    groups: dict[str, dict[str, list[Outcome]]] = {
        "categoria": defaultdict(list),
        "familia": defaultdict(list),
        "complexidade": defaultdict(list),
    }
    for outcome in outcomes:
        groups["categoria"][outcome.gold["category"]].append(outcome)
        groups["familia"][outcome.gold["template_family"]].append(outcome)
        groups["complexidade"][outcome.gold["complexity"]].append(outcome)
    by_category = {name: _group_summary(members) for name, members in groups["categoria"].items()}
    weighted = sum(REAL_MIX[name] * summary["taxa_de_acerto_processo"] for name, summary in by_category.items())
    return {
        "global": _group_summary(outcomes),
        "acerto_ponderado_pela_composicao_real": round(weighted, 4),
        "por_categoria": by_category,
        "por_familia_de_template": {name: _group_summary(members) for name, members in groups["familia"].items()},
        "por_complexidade": {name: _group_summary(members) for name, members in groups["complexidade"].items()},
        "por_criterio": per_check_scores(outcomes),
        "documentos": document_scores(outcomes),
    }
