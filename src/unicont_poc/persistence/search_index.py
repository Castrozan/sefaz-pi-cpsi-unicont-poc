from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class SearchCriteria:
    text: str = ""
    document_type: str = ""
    cnpj: str = ""
    process_number: str = ""
    minimum_amount: float | None = None
    maximum_amount: float | None = None
    limit: int = 50


def _fts_query(text: str) -> str:
    terms = re.findall(r"\w+", text, re.UNICODE)
    return " ".join(f'"{term}"' for term in terms)


class SearchIndex:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def add_process(self, analysis: dict, pages_by_document: dict[str, list[tuple[int, str]]]) -> None:
        for document in analysis["documents"]:
            fields = document["fields"]
            amount = fields.get("amount", {}).get("value")
            self.connection.execute(
                "INSERT INTO indexed_documents (document_id, process_number, document_type, label, cnpj, amount, nucleus_code) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    document["document_id"],
                    analysis["process_number"],
                    document["document_type"],
                    document["label"],
                    fields.get("cnpj", {}).get("value"),
                    float(amount) if amount is not None else None,
                    analysis["nucleus_code"],
                ),
            )
            for page_number, text in pages_by_document[document["document_id"]]:
                self.connection.execute(
                    "INSERT INTO page_text (document_id, page_number, body) VALUES (?, ?, ?)",
                    (document["document_id"], page_number, text),
                )

    def search(self, criteria: SearchCriteria) -> list[dict]:
        clauses, parameters = [], []
        snippet = "''"
        source = "indexed_documents d"
        if criteria.text.strip():
            source += " JOIN page_text p ON p.document_id = d.document_id"
            clauses.append("page_text MATCH ?")
            parameters.append(_fts_query(criteria.text))
            snippet = "snippet(page_text, 2, '[[', ']]', ' … ', 18)"
        for column, value in (
            ("d.document_type", criteria.document_type),
            ("d.cnpj", criteria.cnpj.strip()),
            ("d.process_number", criteria.process_number.strip()),
        ):
            if value:
                clauses.append(f"{column} = ?")
                parameters.append(value)
        if criteria.minimum_amount is not None:
            clauses.append("d.amount >= ?")
            parameters.append(criteria.minimum_amount)
        if criteria.maximum_amount is not None:
            clauses.append("d.amount <= ?")
            parameters.append(criteria.maximum_amount)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        statement = f"SELECT d.document_id, d.process_number, d.label, d.cnpj, d.amount, {snippet} FROM {source} {where} LIMIT ?"
        rows = self.connection.execute(statement, (*parameters, criteria.limit)).fetchall()
        return [
            {
                "document_id": row[0],
                "process_number": row[1],
                "label": row[2],
                "cnpj": row[3],
                "amount": row[4],
                "snippet": row[5],
            }
            for row in rows
        ]
