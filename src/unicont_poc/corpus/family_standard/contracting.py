from __future__ import annotations

from random import Random
from typing import Any

from unicont_poc.corpus.contract import DocumentDraft
from unicont_poc.corpus.formatting import brazilian_money, long_date, numeric_date
from unicont_poc.domain import DocumentType


def render_preliminary_study(slots: dict[str, Any], random_source: Random) -> DocumentDraft:
    return DocumentDraft(
        "ESTUDO TÉCNICO PRELIMINAR",
        (
            f"Processo nº {slots['process_number']}. Unidade: {slots['organ_name']}.",
            f"1. Descrição da necessidade: {slots['need_text']}.",
            f"2. Solução proposta: {slots['object_text']}.",
            "3. Levantamento de mercado: foram analisadas alternativas disponíveis e a solução selecionada é a mais vantajosa.",
            f"4. Estimativa do valor da contratação: {brazilian_money(slots['estimated_amount'])}.",
            "5. Conclusão: a contratação é viável e atende ao interesse público.",
            f"{slots['signer_name']} – Equipe de Planejamento, {numeric_date(slots['issue_date'])}.",
        ),
    )


def render_reference_terms(slots: dict[str, Any], random_source: Random) -> DocumentDraft:
    return DocumentDraft(
        "TERMO DE REFERÊNCIA",
        (
            f"Processo nº {slots['process_number']}.",
            f"1. DO OBJETO: {slots['object_text']}.",
            "2. DA FUNDAMENTAÇÃO: a contratação decorre do estudo técnico preliminar constante dos autos.",
            "3. DO MODELO DE EXECUÇÃO: conforme cronograma a ser aprovado pela fiscalização.",
            f"4. DO VALOR ESTIMADO: {brazilian_money(slots['estimated_amount'])}.",
            f"{slots['signer_name']}, {numeric_date(slots['issue_date'])}.",
        ),
    )


def render_price_survey(slots: dict[str, Any], random_source: Random) -> DocumentDraft:
    quote_lines = tuple(
        f"Fornecedor {position}: {quote['supplier_name']} – CNPJ {quote['supplier_cnpj']} – "
        f"{brazilian_money(quote['amount'])}"
        for position, quote in enumerate(slots["quotes"], start=1)
    )
    return DocumentDraft(
        "MAPA DE PESQUISA DE PREÇOS",
        (
            f"Processo nº {slots['process_number']}. Data: {numeric_date(slots['issue_date'])}.",
            *quote_lines,
            f"Valor estimado da contratação: {brazilian_money(slots['estimated_amount'])}.",
            f"Responsável: {slots['signer_name']}.",
        ),
    )


def render_proposal(slots: dict[str, Any], random_source: Random) -> DocumentDraft:
    return DocumentDraft(
        "PROPOSTA COMERCIAL",
        (
            f"Proponente: {slots['supplier_name']}, CNPJ {slots['supplier_cnpj']}.",
            f"Referência: Processo nº {slots['process_number']}.",
            f"Objeto: {slots['object_text']}.",
            f"Valor global da proposta: {brazilian_money(slots['amount'])}. Validade de 60 dias.",
            f"Data: {numeric_date(slots['issue_date'])}.",
        ),
    )


def render_legal_opinion(slots: dict[str, Any], random_source: Random) -> DocumentDraft:
    conclusion = {
        "favoravel": "Ante o exposto, opina-se favoravelmente ao prosseguimento do feito.",
        "desfavoravel": f"Ante o exposto, opina-se desfavoravelmente ao prosseguimento em razão de {slots['opinion_detail']}.",
        "ressalva_pendente": f"Ante o exposto, opina-se pelo prosseguimento condicionado à correção de {slots['opinion_detail']}.",
        "recomendacao_atendida": f"Ante o exposto, opina-se favoravelmente, registrando-se {slots['opinion_detail']}.",
    }[slots["opinion_kind"]]
    return DocumentDraft(
        f"PARECER JURÍDICO Nº {slots['opinion_number']}",
        (
            f"Processo nº {slots['process_number']}.",
            "EMENTA: Direito Administrativo. Licitações e contratos. Análise prévia de legalidade. Lei nº 14.133/2021.",
            "Trata-se de consulta sobre a regularidade jurídica da contratação pretendida, instruída com os documentos dos autos.",
            "A análise restringe-se aos aspectos jurídicos, não alcançando questões técnicas ou de conveniência.",
            conclusion,
            f"Teresina, {long_date(slots['issue_date'])}.",
            f"{slots['signer_name']} – Procuradoria Setorial",
        ),
    )


def render_inspector_ordinance(slots: dict[str, Any], random_source: Random) -> DocumentDraft:
    return DocumentDraft(
        f"PORTARIA Nº {slots['ordinance_number']}",
        (
            f"Designa fiscal para o Contrato nº {slots['contract_number']}, Processo nº {slots['process_number']}.",
            f"Art. 1º Fica designado(a) {slots['fiscal_name']} como fiscal do contrato em epígrafe.",
            "Art. 2º Esta portaria entra em vigor na data de sua publicação.",
            f"Teresina, {numeric_date(slots['issue_date'])}. {slots['signer_name']}, Ordenador de Despesas.",
        ),
    )


def render_technical_responsibility(slots: dict[str, Any], random_source: Random) -> DocumentDraft:
    return DocumentDraft(
        f"ANOTAÇÃO DE RESPONSABILIDADE TÉCNICA – ART Nº {slots['art_number']}",
        (
            f"Responsável técnico: {slots['responsible_name']}, registro CREA {slots['registration_number']}.",
            f"Atividade técnica: {slots['description']}.",
            f"Processo: {slots['process_number']}. Data: {numeric_date(slots['issue_date'])}.",
        ),
    )


CONTRACTING_RENDERERS = {
    DocumentType.ESTUDO_TECNICO_PRELIMINAR: render_preliminary_study,
    DocumentType.TERMO_REFERENCIA: render_reference_terms,
    DocumentType.PESQUISA_PRECOS: render_price_survey,
    DocumentType.PROPOSTA: render_proposal,
    DocumentType.PARECER_JURIDICO: render_legal_opinion,
    DocumentType.PORTARIA_FISCAL: render_inspector_ordinance,
    DocumentType.ART: render_technical_responsibility,
}
