from __future__ import annotations

from datetime import datetime, timezone

from unicont_poc.domain import ReviewState
from unicont_poc.persistence.store import AnalysisStore
from unicont_poc.ports import SincinPlusGateway


class ReviewRejected(ValueError):
    pass


class AnalystReview:
    def __init__(self, store: AnalysisStore, sincin_gateway: SincinPlusGateway) -> None:
        self.store = store
        self.sincin_gateway = sincin_gateway

    def decide(
        self, process_number: str, analyst_name: str, approve: bool, final_opinion: str, note: str = ""
    ) -> str | None:
        analysis = self.store.analysis(process_number)
        if analysis is None:
            raise ReviewRejected("Processo não encontrado.")
        if analysis["review_state"] != ReviewState.AGUARDANDO_ANALISTA.value:
            raise ReviewRejected("Processo já decidido.")
        if not analyst_name.strip():
            raise ReviewRejected("A decisão exige a identificação do analista.")
        if approve and not final_opinion.strip():
            raise ReviewRejected("A aprovação exige o texto do parecer.")
        if not approve and not note.strip():
            raise ReviewRejected("A devolução exige justificativa.")
        decided_at = datetime.now(timezone.utc).isoformat()
        state = ReviewState.APROVADO if approve else ReviewState.DEVOLVIDO
        self.store.connection.execute(
            "UPDATE analyses SET review_state = ?, analyst_name = ?, analyst_note = ?, decided_at = ? WHERE process_number = ?",
            (state.value, analyst_name.strip(), note.strip(), decided_at, process_number),
        )
        self.store.ledger.append(
            "decisao_do_analista",
            process_number,
            {
                "analysis_id": analysis["analysis_id"],
                "analyst_name": analyst_name.strip(),
                "decision": state.value,
                "note": note.strip(),
                "edited_opinion": final_opinion.strip() != analysis["opinion_draft"].strip(),
                "final_opinion": final_opinion,
                "decided_at": decided_at,
            },
        )
        protocol = None
        if approve:
            protocol = self.sincin_gateway.publish_approved_opinion(
                {
                    "process_number": process_number,
                    "analysis_id": analysis["analysis_id"],
                    "analyst_name": analyst_name.strip(),
                    "opinion": final_opinion,
                    "decided_at": decided_at,
                    "checks": [{"code": check["code"], "status": check["status"]} for check in analysis["checks"]],
                }
            )
        self.store.connection.commit()
        return protocol
