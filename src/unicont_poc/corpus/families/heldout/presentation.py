from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from random import Random
from typing import Iterable

from unicont_poc.corpus.formatting import brazilian_money, long_date, numeric_date

CNPJ_DIGIT_COUNT = 14
MONEY_TEMPLATES = ("R$ {number}", "R${number}", "{number} reais", "BRL {number}")
CNPJ_TAG_TEMPLATES = ("CNPJ/MF nº {number}", "C.N.P.J. {number}", "CNPJ {number}", "CNPJ: {number}")
COMPANY_TEMPLATES = (
    "{name}, inscrita no CNPJ/MF sob o nº {number}",
    "{name} (C.N.P.J. {number})",
    "{name} (CNPJ {number})",
    "{name}, CNPJ nº {number}",
)
DATE_STYLE_COUNT = 3


def unpunctuated(text: str) -> str:
    return text.strip().rstrip(".;:,")


@dataclass(frozen=True)
class ValueFormatter:
    money_style: int
    date_style: int
    cnpj_style: int

    @classmethod
    def sample(cls, random_source: Random) -> ValueFormatter:
        return cls(
            money_style=random_source.randrange(len(MONEY_TEMPLATES)),
            date_style=random_source.randrange(DATE_STYLE_COUNT),
            cnpj_style=random_source.randrange(len(COMPANY_TEMPLATES)),
        )

    def money(self, amount: Decimal) -> str:
        number = brazilian_money(amount).removeprefix("R$ ")
        return MONEY_TEMPLATES[self.money_style].format(number=number)

    def calendar_date(self, value: date) -> str:
        if self.date_style == 0:
            return numeric_date(value)
        if self.date_style == 1:
            return long_date(value)
        return numeric_date(value).replace("/", ".")

    def cnpj(self, raw_cnpj: str) -> str:
        digits = re.sub(r"\D", "", raw_cnpj)
        if len(digits) != CNPJ_DIGIT_COUNT:
            return raw_cnpj
        return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"

    def cnpj_tag(self, raw_cnpj: str) -> str:
        return CNPJ_TAG_TEMPLATES[self.cnpj_style].format(number=self.cnpj(raw_cnpj))

    def company(self, name: str, raw_cnpj: str) -> str:
        return COMPANY_TEMPLATES[self.cnpj_style].format(name=name, number=self.cnpj(raw_cnpj))

    @staticmethod
    def joined(items: Iterable[object]) -> str:
        texts = [str(item) for item in items]
        if len(texts) == 1:
            return texts[0]
        return ", ".join(texts[:-1]) + " e " + texts[-1]
