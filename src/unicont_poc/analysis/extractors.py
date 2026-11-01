from __future__ import annotations

import re
from collections.abc import Callable

from unicont_poc.analysis.parsing import (
    Match,
    PROCESS_NUMBER_PATTERN,
    excerpt,
    find_cnpjs,
    find_dates,
    find_money,
    fold,
    nearest_after_label,
)
from unicont_poc.domain import ClassifiedDocument, DocumentType, Evidence, ExtractedField

PUBLIC_BODY_LABELS = r"tomador|contratante|concedente|unidade gestora|orgao"
PARTY_LABELS = r"emitente|prestador|contratada|credor|favorecido|proponente|convenente|cnpj"
AMOUNT_LABELS: dict[DocumentType, str] = {
    DocumentType.NOTA_FISCAL: r"valor (total|liquido|da nota|do servico)|total da nota",
    DocumentType.NOTA_EMPENHO: r"valor (empenhado|do empenho|reforcado)|importancia",
    DocumentType.LIQUIDACAO: r"valor liquidado|valor da liquidacao",
    DocumentType.ORDEM_PAGAMENTO: r"valor (pago|da ordem|a pagar)",
    DocumentType.CONTRATO: r"valor (global|total|do contrato)",
    DocumentType.PROPOSTA: r"valor (global|total|da proposta)",
    DocumentType.ESTUDO_TECNICO_PRELIMINAR: r"(valor|estimativa).{0,40}(estimad|contratacao)",
    DocumentType.TERMO_REFERENCIA: r"valor estimado|estimativa",
    DocumentType.PESQUISA_PRECOS: r"valor estimado|preco de referencia|valor de referencia",
    DocumentType.TERMO_CONVENIO: r"do valor|valor (global|total|do convenio)",
    DocumentType.PLANO_TRABALHO: r"valor (total|global)",
    DocumentType.RELACAO_PAGAMENTOS: r"total declarado|total geral|total das despesas",
    DocumentType.COMPROVANTE_DEVOLUCAO: r"valor devolvido|valor recolhido",
}
DATE_LABELS: dict[str, str] = {
    "issue_date": r"data de emissao|emitid[oa] em|emissao|data:|data de|teresina,",
    "payment_date": r"data de pagamento|data do pagamento|pag[oa] em",
    "valid_until": r"valid[ao] ate|validade|vencimento",
    "delivered_on": r"protocolad[oa] em|entregue em|apresentad[oa] em|recebid[oa] em",
    "report_deadline": r"prestacao de contas|prazo",
}
EXPENSE_ROW_WIDTH = 240
Extractor = Callable[[ClassifiedDocument], None]


def _record(classified: ClassifiedDocument, name: str, value: object, start: int, end: int) -> None:
    text = classified.document.canonical_text
    quote = excerpt(text, start, end)
    page_number = _page_of(classified, start)
    classified.fields[name] = ExtractedField(
        value, Evidence(classified.document.document_id, page_number, quote, classified.label)
    )


def _page_of(classified: ClassifiedDocument, offset: int) -> int:
    consumed = 0
    for page in classified.document.pages:
        consumed += len(page.canonical_text) + 1
        if offset < consumed:
            return page.page_number
    return classified.document.pages[-1].page_number


def _extract_process_number(classified: ClassifiedDocument) -> None:
    text = classified.document.canonical_text
    found = PROCESS_NUMBER_PATTERN.search(text)
    if found:
        _record(classified, "process_number", found.group(), found.start(), found.end())


def _extract_amount(classified: ClassifiedDocument) -> None:
    text = classified.document.canonical_text
    candidates = find_money(text)
    if not candidates:
        return
    labels = AMOUNT_LABELS.get(classified.document_type)
    chosen = nearest_after_label(text, labels, candidates) if labels else None
    if chosen is None and labels and len(candidates) == 1:
        chosen = candidates[0]
    if chosen:
        _record(classified, "amount", chosen.value, chosen.start, chosen.end)


def _private_party_cnpjs(text: str) -> list[Match]:
    folded = fold(text)
    private = []
    for match in find_cnpjs(text):
        preceding = folded[max(0, match.start - 110) : match.start]
        labels = re.findall(rf"{PUBLIC_BODY_LABELS}|{PARTY_LABELS}", preceding.replace("cnpj", ""))
        if not labels or not re.fullmatch(PUBLIC_BODY_LABELS, labels[-1]):
            private.append(match)
    return private


def _extract_party(classified: ClassifiedDocument) -> None:
    text = classified.document.canonical_text
    private = _private_party_cnpjs(text)
    if private:
        _record(classified, "cnpj", private[0].value, private[0].start, private[0].end)


def _extract_date(classified: ClassifiedDocument, name: str) -> None:
    text = classified.document.canonical_text
    candidates = find_dates(text)
    chosen = nearest_after_label(text, DATE_LABELS[name], candidates, window=60)
    if chosen is None and name == "issue_date" and candidates:
        chosen = candidates[0]
    if chosen:
        _record(classified, name, chosen.value, chosen.start, chosen.end)


def _capture(classified: ClassifiedDocument, name: str, pattern: str) -> None:
    text = classified.document.canonical_text
    found = re.search(pattern, fold(text))
    if found:
        start, end = found.span(1)
        _record(classified, name, text[start:end].strip(" .;"), start, end)


def _extract_invoice(classified: ClassifiedDocument) -> None:
    _capture(classified, "invoice_number", r"nota fiscal[^\d]{0,40}?n[o°º.]*\s*(\d{3,9})")
    _capture(classified, "description", r"discriminacao[^:]*:\s*(.{5,160}?)(?:\.|processo|valor)")


def _extract_object(classified: ClassifiedDocument) -> None:
    _capture(classified, "object_text", r"(?:objeto[^:.]*[:.]|tem por objeto)\s*(.{10,220}?)\.")


def _extract_contract(classified: ClassifiedDocument) -> None:
    _extract_object(classified)
    _capture(classified, "fiscal_name", r"fiscalizacao caber[a] a ([a-z][a-z ]{8,70}?),")
    _capture(classified, "contract_number", r"contrato n[o°º.]*\s*(\d{1,4}/\d{4})")
    text = classified.document.canonical_text
    for name, pattern in (("start_date", r"vigencia de"), ("end_date", r"vigencia de .{10,14} a")):
        found = re.search(pattern, fold(text))
        if found:
            dates = [match for match in find_dates(text) if match.start >= found.end() - 2]
            if dates:
                _record(classified, name, dates[0].value, dates[0].start, dates[0].end)


def _extract_agreement(classified: ClassifiedDocument) -> None:
    _extract_object(classified)
    text = classified.document.canonical_text
    found = re.search(r"vigencia", fold(text))
    if found:
        dates = [match for match in find_dates(text) if match.start >= found.start()]
        if len(dates) >= 2:
            _record(classified, "start_date", dates[0].value, dates[0].start, dates[0].end)
            _record(classified, "end_date", dates[1].value, dates[1].start, dates[1].end)
    _extract_date(classified, "report_deadline")


def _extract_statement_balances(classified: ClassifiedDocument) -> None:
    text = classified.document.canonical_text
    closing = nearest_after_label(text, r"saldo final", find_money(text))
    if closing:
        _record(classified, "closing_balance", closing.value, closing.start, closing.end)


def _extract_expenses(classified: ClassifiedDocument) -> None:
    text = classified.document.canonical_text
    amounts = find_money(text)
    dates = find_dates(text)
    rows = []
    for position, row_date in enumerate(dates):
        limit = dates[position + 1].start if position + 1 < len(dates) else len(text)
        row_amounts = [
            match
            for match in amounts
            if row_date.end <= match.start < limit and match.start - row_date.end < EXPENSE_ROW_WIDTH
        ]
        if row_amounts:
            rows.append(
                {
                    "date": row_date.value,
                    "amount": row_amounts[0].value,
                    "line": text[row_date.start : row_amounts[0].end],
                }
            )
    if rows:
        classified.fields["expenses"] = ExtractedField(
            rows, Evidence(classified.document.document_id, 1, rows[0]["line"], classified.label)
        )


TYPE_EXTRACTORS: dict[DocumentType, tuple[Extractor, ...]] = {
    DocumentType.NOTA_FISCAL: (_extract_invoice, lambda c: _extract_date(c, "issue_date")),
    DocumentType.NOTA_EMPENHO: (lambda c: _extract_date(c, "issue_date"),),
    DocumentType.ORDEM_PAGAMENTO: (lambda c: _extract_date(c, "payment_date"),),
    DocumentType.CONTRATO: (_extract_contract,),
    DocumentType.TERMO_REFERENCIA: (_extract_object,),
    DocumentType.PROPOSTA: (_extract_object,),
    DocumentType.TERMO_CONVENIO: (_extract_agreement,),
    DocumentType.PLANO_TRABALHO: (_extract_object,),
    DocumentType.RELATORIO_EXECUCAO: (lambda c: _extract_date(c, "delivered_on"),),
    DocumentType.RELACAO_PAGAMENTOS: (_extract_expenses,),
    DocumentType.EXTRATO_BANCARIO: (_extract_statement_balances,),
    DocumentType.CERTIDAO_FEDERAL: (lambda c: _extract_date(c, "valid_until"),),
    DocumentType.CERTIDAO_FGTS: (lambda c: _extract_date(c, "valid_until"),),
    DocumentType.CERTIDAO_TRABALHISTA: (lambda c: _extract_date(c, "valid_until"),),
}


def extract_fields(classified: ClassifiedDocument) -> None:
    classified.fields.clear()
    _extract_process_number(classified)
    _extract_amount(classified)
    _extract_party(classified)
    for extractor in TYPE_EXTRACTORS.get(classified.document_type, ()):
        extractor(classified)
