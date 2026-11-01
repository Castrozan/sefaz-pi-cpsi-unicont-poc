from __future__ import annotations

from random import Random
from typing import Any

from unicont_poc.corpus.contract import DocumentDraft
from unicont_poc.corpus.formatting import brazilian_money, long_date, numeric_date
from unicont_poc.domain import DocumentType

CONTRACT_CLAUSES = (
    "CLÁUSULA SEGUNDA – DA VIGÊNCIA. O prazo de vigência é o indicado neste instrumento, admitida a prorrogação na forma da lei.",
    "CLÁUSULA TERCEIRA – DO PAGAMENTO. O pagamento será efetuado após a liquidação da despesa, mediante nota fiscal atestada.",
    "CLÁUSULA QUARTA – DAS OBRIGAÇÕES. A CONTRATADA manterá as condições de habilitação durante toda a execução contratual.",
    "CLÁUSULA QUINTA – DA FISCALIZAÇÃO. A execução será acompanhada por representante da Administração especialmente designado.",
    "CLÁUSULA SEXTA – DAS SANÇÕES. O descumprimento sujeitará a CONTRATADA às penalidades previstas na Lei nº 14.133/2021.",
)
CERTIFICATE_TITLES = {
    DocumentType.CERTIDAO_FEDERAL: "CERTIDÃO NEGATIVA DE DÉBITOS RELATIVOS A TRIBUTOS FEDERAIS E À DÍVIDA ATIVA DA UNIÃO",
    DocumentType.CERTIDAO_FGTS: "CERTIFICADO DE REGULARIDADE DO FGTS – CRF",
    DocumentType.CERTIDAO_TRABALHISTA: "CERTIDÃO NEGATIVA DE DÉBITOS TRABALHISTAS",
}


def render_invoice(slots: dict[str, Any], random_source: Random) -> DocumentDraft:
    return DocumentDraft(
        f"NOTA FISCAL DE SERVIÇOS ELETRÔNICA Nº {slots['invoice_number']}",
        (
            f"Emitente: {slots['supplier_name']} – CNPJ {slots['supplier_cnpj']}",
            f"Tomador: {slots['organ_name']} – CNPJ {slots['organ_cnpj']}",
            f"Data de emissão: {numeric_date(slots['issue_date'])}",
            f"Discriminação: {slots['description']}.",
            f"Processo de origem: {slots['process_number']}",
            f"Valor total da nota: {brazilian_money(slots['amount'])}",
        ),
    )


def render_attestation(slots: dict[str, Any], random_source: Random) -> DocumentDraft:
    numbers = ", ".join(slots["invoice_numbers"])
    statement = "Atesto que os serviços e materiais foram recebidos integralmente, conforme o contrato, sem ressalvas."
    if slots["statement_kind"] == "ressalva_execucao":
        statement = f"Atesto o recebimento com a seguinte observação: {slots['exception_detail']}."
    if slots["statement_kind"] == "ressalva_afastada":
        statement = f"Atesto o recebimento integral. Consigno que {slots['exception_detail']}, nada havendo a glosar."
    return DocumentDraft(
        "ATESTO DE RECEBIMENTO",
        (
            f"Processo nº {slots['process_number']}, Contrato nº {slots['contract_number']}.",
            f"Referente à(s) nota(s) fiscal(is) nº {numbers}, relativas a {slots['service_summary']}.",
            statement,
            f"Teresina, {numeric_date(slots['issue_date'])}.",
            f"{slots['attesting_name']} – {slots['attesting_role']}",
        ),
    )


def render_commitment(slots: dict[str, Any], random_source: Random) -> DocumentDraft:
    return DocumentDraft(
        f"NOTA DE EMPENHO Nº {slots['commitment_number']}",
        (
            f"Tipo: {'Reforço' if slots['kind'] == 'reforco' else 'Ordinário'}",
            f"Data de emissão: {numeric_date(slots['issue_date'])}",
            f"Unidade gestora: {slots['organ_name']}",
            f"Credor: {slots['supplier_name']} – CNPJ {slots['supplier_cnpj']}",
            f"Natureza da despesa: {slots['budget_line']}",
            f"Histórico: {slots['description']}.",
            f"Valor empenhado: {brazilian_money(slots['amount'])}",
            f"Processo: {slots['process_number']}",
        ),
    )


def render_settlement(slots: dict[str, Any], random_source: Random) -> DocumentDraft:
    return DocumentDraft(
        f"NOTA DE LIQUIDAÇÃO Nº {slots['settlement_number']}",
        (
            f"Processo: {slots['process_number']}",
            f"Empenho: {slots['commitment_number']}. Documentos fiscais: {', '.join(slots['invoice_numbers'])}.",
            f"Credor: {slots['supplier_name']} – CNPJ {slots['supplier_cnpj']}",
            f"Data: {numeric_date(slots['issue_date'])}",
            f"Valor liquidado: {brazilian_money(slots['amount'])}",
        ),
    )


def render_payment_order(slots: dict[str, Any], random_source: Random) -> DocumentDraft:
    return DocumentDraft(
        f"ORDEM BANCÁRIA Nº {slots['payment_order_number']}",
        (
            f"Processo: {slots['process_number']}",
            f"Favorecido: {slots['supplier_name']} – CNPJ {slots['supplier_cnpj']}",
            f"Domicílio bancário: {slots['bank_account']}",
            f"Data de pagamento: {numeric_date(slots['issue_date'])}",
            f"Valor pago: {brazilian_money(slots['amount'])}",
        ),
    )


def render_contract(slots: dict[str, Any], random_source: Random) -> DocumentDraft:
    fiscal_clause = (
        f"A fiscalização caberá a {slots['fiscal_name']}, designado por portaria própria."
        if slots["fiscal_name"]
        else "A fiscalização caberá a servidor a ser oportunamente indicado."
    )
    return DocumentDraft(
        f"CONTRATO Nº {slots['contract_number']}",
        (
            f"CONTRATANTE: {slots['organ_name']}, CNPJ {slots['organ_cnpj']}.",
            f"CONTRATADA: {slots['supplier_name']}, CNPJ {slots['supplier_cnpj']}.",
            f"Processo administrativo nº {slots['process_number']}.",
            f"CLÁUSULA PRIMEIRA – DO OBJETO. O presente contrato tem por objeto {slots['object_text']}.",
            f"Valor global: {brazilian_money(slots['amount'])}. "
            f"Vigência de {numeric_date(slots['start_date'])} a {numeric_date(slots['end_date'])}.",
            *CONTRACT_CLAUSES,
            fiscal_clause,
            f"Teresina, {long_date(slots['issue_date'])}.",
            f"{slots['signer_name']} – Ordenador de Despesas",
        ),
    )


def render_certificate(document_type: DocumentType):
    def render(slots: dict[str, Any], random_source: Random) -> DocumentDraft:
        return DocumentDraft(
            CERTIFICATE_TITLES[document_type],
            (
                f"Nome: {slots['supplier_name']}",
                f"CNPJ: {slots['supplier_cnpj']}",
                "Certifica-se que não constam pendências em nome do sujeito acima identificado.",
                f"Emitida em {numeric_date(slots['issue_date'])}.",
                f"Válida até {numeric_date(slots['valid_until'])}.",
                f"Código de controle: {slots['certificate_code']}",
            ),
        )

    return render


PAYMENT_RENDERERS = {
    DocumentType.NOTA_FISCAL: render_invoice,
    DocumentType.ATESTO: render_attestation,
    DocumentType.NOTA_EMPENHO: render_commitment,
    DocumentType.LIQUIDACAO: render_settlement,
    DocumentType.ORDEM_PAGAMENTO: render_payment_order,
    DocumentType.CONTRATO: render_contract,
    **{document_type: render_certificate(document_type) for document_type in CERTIFICATE_TITLES},
}
