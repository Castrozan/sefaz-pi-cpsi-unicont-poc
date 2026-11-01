from datetime import date
from decimal import Decimal

from unicont_poc.analysis.parsing import excerpt, find_cnpjs, find_dates, find_money, fold


def test_fold_preserves_length_so_offsets_map_back_to_the_original():
    text = "Certidão de Regularidade – Ação"
    assert len(fold(text)) == len(text)
    assert fold("Certidão") == "certidao"


def test_money_formats_common_in_brazilian_documents():
    values = [match.value for match in find_money("R$ 1.234,56 e R$1.234,56 e 1.234,56 reais e BRL 9,90")]
    assert values == [Decimal("1234.56"), Decimal("1234.56"), Decimal("1234.56"), Decimal("9.90")]


def test_cnpj_with_invalid_check_digits_is_rejected():
    assert [match.value for match in find_cnpjs("CNPJ 11.222.333/0001-81")] == ["11.222.333/0001-81"]
    assert find_cnpjs("CNPJ 11.222.333/0001-82") == []


def test_dates_numeric_dotted_and_long():
    found = [match.value for match in find_dates("03/05/2026, 03.05.2026 e 3 de março de 2026")]
    assert found == [date(2026, 5, 3), date(2026, 5, 3), date(2026, 3, 3)]


def test_impossible_date_is_ignored():
    assert find_dates("31/02/2026") == []


def test_excerpt_does_not_cut_words():
    text = "alfa beta gama delta epsilon zeta eta teta iota kapa"
    assert excerpt(text, 21, 28, margin=9) == "delta epsilon zeta"
