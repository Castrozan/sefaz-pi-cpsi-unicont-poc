from __future__ import annotations

from typing import Protocol
from urllib.parse import quote

CORPUS_RELEASE_URL = "https://github.com/Castrozan/sefaz-pi-cpsi-unicont-poc/releases/tag/avaliacao-1"


def _encoded(value: str) -> str:
    return quote(value, safe="/")


def process_slug(process_number: str) -> str:
    return process_number.replace("/", "-")


class Routes(Protocol):
    decision_action: str
    document_original_label: str

    def asset(self, name: str) -> str: ...
    def queue(self, nucleus_code: str = "") -> str: ...
    def search(self) -> str: ...
    def dashboard(self) -> str: ...
    def evaluation(self) -> str: ...
    def process(self, process_number: str) -> str: ...
    def audit(self, process_number: str) -> str: ...
    def document(self, document_id: str, quote_text: str = "") -> str: ...
    def document_original(self, document_id: str) -> str: ...


class ServerRoutes:
    decision_action = "/processo/decisao"
    document_original_label = "PDF original"

    def asset(self, name: str) -> str:
        return f"/estatico/{name}"

    def queue(self, nucleus_code: str = "") -> str:
        return f"/?nucleo={_encoded(nucleus_code)}" if nucleus_code else "/"

    def search(self) -> str:
        return "/busca"

    def dashboard(self) -> str:
        return "/painel"

    def evaluation(self) -> str:
        return "/avaliacao"

    def process(self, process_number: str) -> str:
        return f"/processo?numero={_encoded(process_number)}"

    def audit(self, process_number: str) -> str:
        return f"/auditoria?numero={_encoded(process_number)}"

    def document(self, document_id: str, quote_text: str = "") -> str:
        suffix = f"?trecho={_encoded(quote_text)}#citacao" if quote_text else ""
        return f"/documento/{document_id}{suffix}"

    def document_original(self, document_id: str) -> str:
        return f"/documento/{document_id}/original"


class StaticRoutes:
    decision_action = ""
    document_original_label = "PDF original, no corpus publicado"

    def __init__(self, base_path: str) -> None:
        self.base_path = base_path.rstrip("/")

    def asset(self, name: str) -> str:
        return f"{self.base_path}/estatico/{name}"

    def queue(self, nucleus_code: str = "") -> str:
        suffix = f"?nucleo={_encoded(nucleus_code)}" if nucleus_code else ""
        return f"{self.base_path}/{suffix}"

    def search(self) -> str:
        return f"{self.base_path}/busca/"

    def dashboard(self) -> str:
        return f"{self.base_path}/painel/"

    def evaluation(self) -> str:
        return f"{self.base_path}/avaliacao/"

    def process(self, process_number: str) -> str:
        return f"{self.base_path}/processo/{process_slug(process_number)}/"

    def audit(self, process_number: str) -> str:
        return f"{self.base_path}/auditoria/{process_slug(process_number)}/"

    def document(self, document_id: str, quote_text: str = "") -> str:
        suffix = f"?trecho={_encoded(quote_text)}#citacao" if quote_text else ""
        return f"{self.base_path}/documento/{document_id}/{suffix}"

    def document_original(self, document_id: str) -> str:
        return CORPUS_RELEASE_URL
