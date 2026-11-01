from __future__ import annotations

import hashlib
import json
import sqlite3

GENESIS_HASH = "0" * 64


def _chain_hash(previous_hash: str, event_type: str, process_number: str, payload_json: str) -> str:
    return hashlib.sha256(f"{previous_hash}|{event_type}|{process_number}|{payload_json}".encode()).hexdigest()


class AuditLedger:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def append(self, event_type: str, process_number: str, payload: dict) -> str:
        last = self.connection.execute("SELECT entry_hash FROM audit_ledger ORDER BY sequence DESC LIMIT 1").fetchone()
        previous_hash = last[0] if last else GENESIS_HASH
        payload_json = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        entry_hash = _chain_hash(previous_hash, event_type, process_number, payload_json)
        self.connection.execute(
            "INSERT INTO audit_ledger (event_type, process_number, payload, previous_hash, entry_hash) VALUES (?, ?, ?, ?, ?)",
            (event_type, process_number, payload_json, previous_hash, entry_hash),
        )
        return entry_hash

    def verify_chain(self) -> tuple[bool, int]:
        previous_hash = GENESIS_HASH
        rows = self.connection.execute(
            "SELECT sequence, event_type, process_number, payload, previous_hash, entry_hash FROM audit_ledger ORDER BY sequence"
        ).fetchall()
        for sequence, event_type, process_number, payload_json, stored_previous, stored_hash in rows:
            expected_hash = _chain_hash(previous_hash, event_type, process_number, payload_json)
            if stored_previous != previous_hash or expected_hash != stored_hash:
                return False, sequence
            previous_hash = stored_hash
        return True, len(rows)

    def entries_for(self, process_number: str) -> list[dict]:
        rows = self.connection.execute(
            "SELECT sequence, event_type, payload, entry_hash FROM audit_ledger WHERE process_number = ? ORDER BY sequence",
            (process_number,),
        ).fetchall()
        return [
            {"sequence": sequence, "event_type": event_type, "payload": json.loads(payload), "entry_hash": entry_hash}
            for sequence, event_type, payload, entry_hash in rows
        ]
