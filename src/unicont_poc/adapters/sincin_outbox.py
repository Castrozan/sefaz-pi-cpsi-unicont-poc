from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from unicont_poc.domain import ReviewState
from unicont_poc.persistence.store import AnalysisStore


class NotApprovedByAnalyst(PermissionError):
    pass


class SincinOutboxStub:
    def __init__(self, store: AnalysisStore) -> None:
        self.store = store

    def publish_approved_opinion(self, opinion: dict) -> str:
        row = self.store.connection.execute(
            "SELECT review_state FROM analyses WHERE process_number = ?", (opinion["process_number"],)
        ).fetchone()
        if row is None or row[0] != ReviewState.APROVADO.value:
            raise NotApprovedByAnalyst(opinion["process_number"])
        payload = json.dumps(opinion, ensure_ascii=False, sort_keys=True)
        protocol = "STUB-" + hashlib.sha256(payload.encode()).hexdigest()[:12].upper()
        self.store.connection.execute(
            "INSERT OR REPLACE INTO sincin_outbox (process_number, protocol, payload, sent_at) VALUES (?, ?, ?, ?)",
            (opinion["process_number"], protocol, payload, datetime.now(timezone.utc).isoformat()),
        )
        return protocol
