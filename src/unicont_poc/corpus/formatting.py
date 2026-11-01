from __future__ import annotations

from datetime import date
from decimal import Decimal

MONTH_NAMES = (
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
)


def brazilian_money(amount: Decimal) -> str:
    whole_and_cents = f"{amount:,.2f}"
    return "R$ " + whole_and_cents.replace(",", "X").replace(".", ",").replace("X", ".")


def numeric_date(value: date) -> str:
    return value.strftime("%d/%m/%Y")


def long_date(value: date) -> str:
    return f"{value.day} de {MONTH_NAMES[value.month - 1]} de {value.year}"
