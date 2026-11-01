from __future__ import annotations

from unicont_poc.analysis.checks.accountability import ACCOUNTABILITY_CHECKS
from unicont_poc.analysis.checks.contracting import CONTRACTING_CHECKS
from unicont_poc.analysis.checks.payment import PAYMENT_CHECKS
from unicont_poc.analysis.process_view import ProcessView
from unicont_poc.domain import CheckResult, ProcessCategory

CHECKS_BY_CATEGORY = {
    ProcessCategory.PAGAMENTO: PAYMENT_CHECKS,
    ProcessCategory.CONTRATACAO: CONTRACTING_CHECKS,
    ProcessCategory.PRESTACAO_DE_CONTAS: ACCOUNTABILITY_CHECKS,
}


def run_checks(view: ProcessView) -> list[CheckResult]:
    return [check(view) for check in CHECKS_BY_CATEGORY[view.process.category]]
