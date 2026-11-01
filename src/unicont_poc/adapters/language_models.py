from __future__ import annotations

import hashlib
import json
from pathlib import Path

from unicont_poc.ports import LanguageReply, LanguageRequest

DEFAULT_CLAUDE_MODEL = "claude-sonnet-5-5"


class MissingCachedReply(LookupError):
    pass


def request_key(request: LanguageRequest) -> str:
    return hashlib.sha256(f"{request.system_prompt}\n\n{request.user_prompt}".encode()).hexdigest()


class AnthropicMessagesModel:
    def __init__(self, model_identifier: str = DEFAULT_CLAUDE_MODEL, client: object | None = None) -> None:
        self.model_identifier = model_identifier
        self.client = client

    def _resolved_client(self) -> object:
        if self.client is None:
            import anthropic

            self.client = anthropic.Anthropic()
        return self.client

    def complete(self, request: LanguageRequest) -> LanguageReply:
        message = self._resolved_client().messages.create(
            model=self.model_identifier,
            max_tokens=request.maximum_output_tokens,
            system=request.system_prompt,
            messages=[{"role": "user", "content": request.user_prompt}],
        )
        text = "".join(block.text for block in message.content if block.type == "text")
        return LanguageReply(text, message.model, "api-anthropic")


class ReplayLanguageModel:
    def __init__(self, cache_path: Path) -> None:
        self.replies: dict[str, dict] = {}
        if cache_path.exists():
            for line in cache_path.read_text(encoding="utf-8").splitlines():
                record = json.loads(line)
                self.replies[record["key"]] = record

    def complete(self, request: LanguageRequest) -> LanguageReply:
        record = self.replies.get(request_key(request))
        if record is None:
            raise MissingCachedReply(request_key(request))
        return LanguageReply(record["text"], record["model_identifier"], f"replay:{record['execution_mode']}")


class PromptCollector:
    def __init__(self) -> None:
        self.requests: dict[str, LanguageRequest] = {}

    def complete(self, request: LanguageRequest) -> LanguageReply:
        self.requests[request_key(request)] = request
        return LanguageReply("{}", "coletor", "coleta")
