from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import Decimal

from unicont_poc.domain import CheckResult, CheckStatus, RiskLevel

HIGH_SEVERITY_CODES = {
    "PAG-05",
    "PAG-06",
    "PAG-07",
    "PAG-08",
    "PAG-09",
    "PAG-10",
    "PAG-11",
    "CON-03",
    "CON-05",
    "CON-07",
    "CON-08",
    "CON-09",
    "PRE-03",
    "PRE-04",
    "PRE-05",
    "PRE-07",
}
HIGH_SEVERITY_WEIGHT = 3
STANDARD_WEIGHT = 2
UNVERIFIED_WEIGHT = 1


@dataclass(frozen=True)
class RiskAssessment:
    level: RiskLevel
    priority_score: float
    reasons: tuple[str, ...]


def assess_risk(checks: list[CheckResult], process_value: Decimal | None) -> RiskAssessment:
    failures = [check for check in checks if check.status is CheckStatus.NAO_CONFORME]
    unverified = [check for check in checks if check.status is CheckStatus.NAO_VERIFICAVEL]
    weight = sum(HIGH_SEVERITY_WEIGHT if check.code in HIGH_SEVERITY_CODES else STANDARD_WEIGHT for check in failures)
    weight += UNVERIFIED_WEIGHT * len(unverified)
    level = RiskLevel.BAIXO
    if failures or unverified:
        level = RiskLevel.MEDIO
    if len(failures) >= 2 or any(check.code in HIGH_SEVERITY_CODES for check in failures):
        level = RiskLevel.ALTO
    value_factor = math.log10(float(process_value)) if process_value and process_value > 1 else 1.0
    return RiskAssessment(
        level,
        round(weight * value_factor, 2),
        tuple(f"{check.code}: {check.rationale}" for check in [*failures, *unverified]),
    )
