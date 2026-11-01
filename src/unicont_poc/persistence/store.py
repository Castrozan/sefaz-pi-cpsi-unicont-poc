from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from unicont_poc.domain import ReviewState
from unicont_poc.persistence.audit_ledger import AuditLedger
from unicont_poc.persistence.search_index import SearchIndex

SCHEMA = """
CREATE TABLE IF NOT EXISTS analyses (
    process_number TEXT PRIMARY KEY, category TEXT, nucleus_code TEXT, risk_level TEXT, priority_score REAL,
    verdict TEXT, review_state TEXT, analyst_name TEXT, analyst_note TEXT, decided_at TEXT, record TEXT
);
CREATE TABLE IF NOT EXISTS indexed_documents (
    document_id TEXT PRIMARY KEY, process_number TEXT, document_type TEXT, label TEXT, cnpj TEXT, amount REAL,
    nucleus_code TEXT
);
CREATE INDEX IF NOT EXISTS documents_by_type ON indexed_documents (document_type);
CREATE INDEX IF NOT EXISTS documents_by_cnpj ON indexed_documents (cnpj);
CREATE INDEX IF NOT EXISTS documents_by_process ON indexed_documents (process_number);
CREATE VIRTUAL TABLE IF NOT EXISTS page_text USING fts5(
    document_id UNINDEXED, page_number UNINDEXED, body, tokenize = 'unicode61 remove_diacritics 2'
);
CREATE TABLE IF NOT EXISTS audit_ledger (
    sequence INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT, process_number TEXT, payload TEXT,
    previous_hash TEXT, entry_hash TEXT
);
CREATE INDEX IF NOT EXISTS ledger_by_process ON audit_ledger (process_number);
CREATE TABLE IF NOT EXISTS sincin_outbox (
    process_number TEXT PRIMARY KEY, protocol TEXT, payload TEXT, sent_at TEXT
);
"""


class AnalysisStore:
    def __init__(self, database_path: Path) -> None:
        database_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(database_path, check_same_thread=False)
        self.connection.executescript(SCHEMA)
        self.ledger = AuditLedger(self.connection)
        self.search_index = SearchIndex(self.connection)

    def save_analysis(self, analysis: dict, pages_by_document: dict[str, list[tuple[int, str]]]) -> None:
        self.connection.execute(
            "INSERT OR REPLACE INTO analyses (process_number, category, nucleus_code, risk_level, priority_score, verdict, "
            "review_state, record) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                analysis["process_number"],
                analysis["category"],
                analysis["nucleus_code"],
                analysis["risk"]["level"],
                analysis["risk"]["priority_score"],
                analysis["verdict"],
                ReviewState.AGUARDANDO_ANALISTA.value,
                json.dumps(analysis, ensure_ascii=False),
            ),
        )
        self.search_index.add_process(analysis, pages_by_document)
        self.ledger.append("analise_concluida", analysis["process_number"], analysis)
        self.connection.commit()

    def analysis(self, process_number: str) -> dict | None:
        row = self.connection.execute(
            "SELECT record, review_state, analyst_name, analyst_note, decided_at FROM analyses WHERE process_number = ?",
            (process_number,),
        ).fetchone()
        if row is None:
            return None
        return {
            **json.loads(row[0]),
            "review_state": row[1],
            "analyst_name": row[2],
            "analyst_note": row[3],
            "decided_at": row[4],
        }

    def queue(self, nucleus_code: str = "", risk_level: str = "", review_state: str = "") -> list[dict]:
        clauses, parameters = [], []
        for column, value in (
            ("nucleus_code", nucleus_code),
            ("risk_level", risk_level),
            ("review_state", review_state),
        ):
            if value:
                clauses.append(f"{column} = ?")
                parameters.append(value)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self.connection.execute(
            "SELECT process_number, category, nucleus_code, risk_level, priority_score, verdict, review_state "
            f"FROM analyses {where} ORDER BY priority_score DESC, process_number",
            parameters,
        ).fetchall()
        keys = ("process_number", "category", "nucleus_code", "risk_level", "priority_score", "verdict", "review_state")
        return [dict(zip(keys, row)) for row in rows]

    def all_records(self) -> list[dict]:
        rows = self.connection.execute("SELECT record, review_state FROM analyses").fetchall()
        return [{**json.loads(record), "review_state": state} for record, state in rows]
