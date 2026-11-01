from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

from unicont_poc.domain import AdministrativeProcess, ProcessCategory, SourceDocument
from unicont_poc.ingestion.text_extraction import read_pdf_pages


class SyntheticSeiGateway:
    def __init__(self, corpus_directory: Path) -> None:
        self.corpus_directory = corpus_directory
        manifest_lines = (corpus_directory / "manifesto.jsonl").read_text(encoding="utf-8").splitlines()
        self.manifest = {record["process_number"]: record for record in map(json.loads, manifest_lines)}

    def process_numbers(self) -> list[str]:
        return list(self.manifest)

    def fetch_process(self, process_number: str) -> AdministrativeProcess:
        record = self.manifest[process_number]
        documents = []
        for document in record["documents"]:
            pages, was_scanned, digest = read_pdf_pages(self.corpus_directory / document["path"])
            documents.append(
                SourceDocument(document["document_id"], document["declared_title"], digest, pages, was_scanned)
            )
        return AdministrativeProcess(
            record["process_number"],
            ProcessCategory(record["category"]),
            record["organ_name"],
            record["nucleus_code"],
            tuple(documents),
        )

    def iterate_processes(self) -> Iterator[AdministrativeProcess]:
        for process_number in self.manifest:
            yield self.fetch_process(process_number)
