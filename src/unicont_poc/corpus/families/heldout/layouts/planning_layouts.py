from __future__ import annotations

from unicont_poc.corpus.contract import DocumentDraft
from unicont_poc.corpus.families.heldout.layout_support import LayoutCatalog, Slots, draft
from unicont_poc.corpus.families.heldout.presentation import ValueFormatter, unpunctuated
from unicont_poc.domain import DocumentType


def preliminary_study_sections(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Estudo Técnico Preliminar",
        f"Este estudo técnico preliminar foi elaborado em {view.calendar_date(slots['issue_date'])}.",
        f"1. Descrição da necessidade: {unpunctuated(slots['need_text'])}.",
        f"2. Objeto pretendido: {unpunctuated(slots['object_text'])}.",
        f"3. Estimativa do valor da contratação: {view.money(slots['estimated_amount'])}.",
        f"Responsável pela elaboração: {slots['signer_name']}.",
    )


def preliminary_study_narrative(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "ETP",
        f"Em {view.calendar_date(slots['issue_date'])}, {slots['signer_name']} concluiu o estudo técnico "
        f"preliminar (ETP) que embasa a futura contratação.",
        f"A necessidade administrativa que a motiva é a seguinte: {unpunctuated(slots['need_text'])}. "
        f"O que se pretende contratar é: {unpunctuated(slots['object_text'])}.",
        f"O valor estimado da contratação é de {view.money(slots['estimated_amount'])}.",
    )


def preliminary_study_estimate_first(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Planejamento da Contratação - Estudo Preliminar",
        f"Valor estimado: {view.money(slots['estimated_amount'])}. Objeto: {unpunctuated(slots['object_text'])}.",
        f"Justificativa da necessidade: {unpunctuated(slots['need_text'])}.",
        f"Estudo técnico preliminar assinado por {slots['signer_name']} em {view.calendar_date(slots['issue_date'])}.",
    )


def reference_terms_numbered(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Termo de Referência",
        f"1. DO OBJETO: {unpunctuated(slots['object_text'])}.",
        f"2. DO VALOR ESTIMADO: {view.money(slots['estimated_amount'])}.",
        f"Este termo de referência foi elaborado por {slots['signer_name']} em "
        f"{view.calendar_date(slots['issue_date'])}.",
    )


def reference_terms_narrative(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "TR - Especificação da Contratação",
        f"Constitui objeto deste termo de referência: {unpunctuated(slots['object_text'])}.",
        f"Para fins de planejamento, a contratação foi estimada em {view.money(slots['estimated_amount'])}.",
        f"Elaboração: {slots['signer_name']}, em {view.calendar_date(slots['issue_date'])}.",
    )


def reference_terms_tabular(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Termo de Referência para Contratação",
        f"TERMO DE REFERÊNCIA | DATA {view.calendar_date(slots['issue_date'])}",
        f"OBJETO | {unpunctuated(slots['object_text'])}",
        f"ESTIMATIVA | {view.money(slots['estimated_amount'])}",
        f"RESPONSÁVEL | {slots['signer_name']}",
    )


def price_survey_numbered(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    quotes = slots["quotes"]
    lines = [
        f"Cotação {position}: {view.company(quote['supplier_name'], quote['supplier_cnpj'])} - "
        f"{view.money(quote['amount'])}"
        for position, quote in enumerate(quotes, start=1)
    ]
    return draft(
        "Pesquisa de Preços",
        f"Pesquisa de preços realizada por {slots['signer_name']} em {view.calendar_date(slots['issue_date'])}, "
        f"com {len(quotes)} cotação(ões) obtida(s).",
        *lines,
        f"Valor estimado da contratação: {view.money(slots['estimated_amount'])}.",
    )


def price_survey_tabular(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    rows = [
        f"{quote['supplier_name']} | {view.cnpj_tag(quote['supplier_cnpj'])} | {view.money(quote['amount'])}"
        for quote in slots["quotes"]
    ]
    return draft(
        "Mapa Comparativo de Preços",
        f"MAPA DE PESQUISA DE PREÇOS - {view.calendar_date(slots['issue_date'])} - RESPONSÁVEL: {slots['signer_name']}",
        "FORNECEDOR | INSCRIÇÃO | PREÇO COTADO",
        *rows,
        f"ESTIMATIVA DE REFERÊNCIA (VALOR ESTIMADO) ........ {view.money(slots['estimated_amount'])}",
    )


def price_survey_narrative(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    offers = [
        f"{quote['supplier_name']} ({view.cnpj_tag(quote['supplier_cnpj'])}) ofertou {view.money(quote['amount'])}"
        for quote in slots["quotes"]
    ]
    return draft(
        "Consulta ao Mercado",
        f"Consultaram-se {len(offers)} fornecedor(es) para a pesquisa de preços de "
        f"{view.calendar_date(slots['issue_date'])}, conduzida por {slots['signer_name']}.",
        "; ".join(offers) + ".",
        f"Assim, o valor estimado da contratação ficou em {view.money(slots['estimated_amount'])}.",
    )


def proposal_formal_letter(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    supplier = view.company(slots["supplier_name"], slots["supplier_cnpj"])
    return draft(
        "Proposta Comercial",
        f"Apresenta-se a presente proposta comercial, datada de {view.calendar_date(slots['issue_date'])}, "
        f"para o seguinte objeto: {unpunctuated(slots['object_text'])}.",
        f"Preço global ofertado: {view.money(slots['amount'])}. Proponente: {supplier}.",
    )


def proposal_tabular_form(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Formulário de Proposta de Preços",
        f"PROPONENTE | {slots['supplier_name']} | {view.cnpj_tag(slots['supplier_cnpj'])}",
        f"OBJETO DA PROPOSTA | {unpunctuated(slots['object_text'])}",
        f"VALOR PROPOSTO | {view.money(slots['amount'])}",
        f"DATA DA PROPOSTA | {view.calendar_date(slots['issue_date'])}",
    )


def proposal_price_first(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    return draft(
        "Oferta de Preço",
        f"Oferecemos o objeto abaixo por {view.money(slots['amount'])}: {unpunctuated(slots['object_text'])}.",
        f"Proposta comercial firmada em {view.calendar_date(slots['issue_date'])} por "
        f"{view.company(slots['supplier_name'], slots['supplier_cnpj'])}.",
    )


PLANNING_LAYOUTS: LayoutCatalog = {
    DocumentType.ESTUDO_TECNICO_PRELIMINAR: (
        preliminary_study_sections,
        preliminary_study_narrative,
        preliminary_study_estimate_first,
    ),
    DocumentType.TERMO_REFERENCIA: (reference_terms_numbered, reference_terms_narrative, reference_terms_tabular),
    DocumentType.PESQUISA_PRECOS: (price_survey_numbered, price_survey_tabular, price_survey_narrative),
    DocumentType.PROPOSTA: (proposal_formal_letter, proposal_tabular_form, proposal_price_first),
}
