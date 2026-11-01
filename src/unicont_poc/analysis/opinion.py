from __future__ import annotations

from unicont_poc.domain import CheckResult, CheckStatus

DISCLAIMER = (
    "Minuta preliminar gerada por sistema de apoio, sujeita à revisão e à decisão do analista do Núcleo de Controle "
    "Interno. Não constitui manifestação conclusiva."
)


def overall_verdict(checks: list[CheckResult]) -> str:
    statuses = {check.status for check in checks}
    if CheckStatus.NAO_CONFORME in statuses:
        return "nao_conforme"
    if CheckStatus.NAO_VERIFICAVEL in statuses:
        return "revisao_humana"
    return "conforme"


VERDICT_SENTENCES = {
    "nao_conforme": "Foram identificados indícios de não conformidade, listados abaixo.",
    "revisao_humana": "Não foram identificados indícios de não conformidade, mas há itens que exigem conferência humana.",
    "conforme": "Não foram identificados indícios de não conformidade nos critérios verificados.",
}


def draft_opinion(process_number: str, organ_name: str, summary: str, checks: list[CheckResult]) -> str:
    verdict = overall_verdict(checks)
    findings = [
        f"- {check.code} ({check.legal_basis}): {check.rationale}"
        for check in checks
        if check.status in (CheckStatus.NAO_CONFORME, CheckStatus.NAO_VERIFICAVEL)
    ]
    verified = sum(check.status is CheckStatus.CONFORME for check in checks)
    sections = [
        f"PARECER PRELIMINAR – Processo {process_number} – {organ_name}",
        f"Síntese: {summary}",
        f"Resultado: {VERDICT_SENTENCES[verdict]} Critérios conformes: {verified} de {len(checks)}.",
    ]
    if findings:
        sections.append("Apontamentos:\n" + "\n".join(findings))
    sections.append(DISCLAIMER)
    return "\n\n".join(sections)
