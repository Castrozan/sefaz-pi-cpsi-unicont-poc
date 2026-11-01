from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol

from unicont_poc.domain import AdministrativeProcess


class SeiGateway(Protocol):
    def process_numbers(self) -> list[str]: ...

    def fetch_process(self, process_number: str) -> AdministrativeProcess: ...

    def iterate_processes(self) -> Iterator[AdministrativeProcess]: ...


class SincinPlusGateway(Protocol):
    def publish_approved_opinion(self, opinion: dict) -> str: ...


@dataclass(frozen=True)
class LanguageRequest:
    system_prompt: str
    user_prompt: str
    maximum_output_tokens: int = 1500


@dataclass(frozen=True)
class LanguageReply:
    text: str
    model_identifier: str
    execution_mode: str


class LanguageModel(Protocol):
    def complete(self, request: LanguageRequest) -> LanguageReply: ...
