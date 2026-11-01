from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

MONTHS = {
    "janeiro": 1,
    "fevereiro": 2,
    "marco": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12,
}
MONEY_PATTERN = re.compile(
    r"(?:R\s?\$|BRL)\s*(\d{1,3}(?:\.\d{3})*,\d{2}|\d+,\d{2})|(\d{1,3}(?:\.\d{3})*,\d{2})\s*(?:reais|\(|$)",
    re.IGNORECASE,
)
CNPJ_PATTERN = re.compile(r"\b\d{2}[.\s]?\d{3}[.\s]?\d{3}\s?/\s?\d{4}\s?-\s?\d{2}\b")
PROCESS_NUMBER_PATTERN = re.compile(r"\b\d{5}\.\d{6}/\d{4}-\d{2}\b")
NUMERIC_DATE_PATTERN = re.compile(r"\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})\b")
LONG_DATE_PATTERN = re.compile(r"\b(\d{1,2})\s+de\s+([a-z]+)\s+de\s+(\d{4})\b")


@dataclass(frozen=True)
class Match:
    value: object
    start: int
    end: int


def fold(text: str) -> str:
    return "".join(unicodedata.normalize("NFD", character)[0].lower()[:1] or " " for character in text)


def parse_money_text(text: str) -> Decimal:
    return Decimal(text.replace(".", "").replace(",", "."))


def find_money(text: str) -> list[Match]:
    return [
        Match(parse_money_text(found.group(1) or found.group(2)), found.start(), found.end())
        for found in MONEY_PATTERN.finditer(text)
    ]


def _cnpj_is_valid(digits: str) -> bool:
    for length, weights in ((12, (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)), (13, (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2))):
        remainder = sum(int(digit) * weight for digit, weight in zip(digits, weights)) % 11
        if digits[length] != ("0" if remainder < 2 else str(11 - remainder)):
            return False
    return True


def canonical_cnpj(digits: str) -> str:
    return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:14]}"


def find_cnpjs(text: str) -> list[Match]:
    matches = []
    for found in CNPJ_PATTERN.finditer(text):
        digits = re.sub(r"\D", "", found.group())
        if len(digits) == 14 and _cnpj_is_valid(digits):
            matches.append(Match(canonical_cnpj(digits), found.start(), found.end()))
    return matches


def find_dates(text: str) -> list[Match]:
    matches = []
    for found in NUMERIC_DATE_PATTERN.finditer(text):
        day, month, year = map(int, found.groups())
        matches.extend(_valid_date(year, month, day, found))
    folded = fold(text)
    for found in LONG_DATE_PATTERN.finditer(folded):
        month = MONTHS.get(found.group(2))
        if month:
            matches.extend(_valid_date(int(found.group(3)), month, int(found.group(1)), found))
    return sorted(matches, key=lambda match: match.start)


def _valid_date(year: int, month: int, day: int, found: re.Match) -> list[Match]:
    try:
        return [Match(date(year, month, day), found.start(), found.end())]
    except ValueError:
        return []


def nearest_after_label(text: str, label_pattern: str, candidates: list[Match], window: int = 90) -> Match | None:
    folded = fold(text)
    for label in re.finditer(label_pattern, folded):
        reachable = [match for match in candidates if label.start() <= match.start <= label.end() + window]
        if reachable:
            return min(reachable, key=lambda match: match.start)
    return None


def excerpt(text: str, start: int, end: int, margin: int = 70) -> str:
    window_start = max(0, start - margin)
    window_end = min(len(text), end + margin)
    if window_start and " " in text[window_start:start]:
        window_start = text.index(" ", window_start) + 1
    if window_end < len(text) and " " in text[end:window_end]:
        window_end = text.rindex(" ", end, window_end)
    return text[window_start:window_end].strip()


def word_bounded_prefix(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: text.rfind(" ", 0, limit) if " " in text[:limit] else limit]
