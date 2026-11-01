from __future__ import annotations

from dataclasses import dataclass

from unicont_poc.corpus.contract import DocumentDraft
from unicont_poc.corpus.families.heldout.layout_support import Layout, LayoutCatalog, Slots, draft
from unicont_poc.corpus.families.heldout.presentation import ValueFormatter
from unicont_poc.domain import DocumentType


@dataclass(frozen=True)
class CertificateProfile:
    official_name: str
    alternative_name: str
    regularity_statement: str


CERTIFICATE_PROFILES = {
    DocumentType.CERTIDAO_FEDERAL: CertificateProfile(
        "Certidão Negativa de Débitos Relativos aos Créditos Tributários Federais e à Dívida Ativa da União",
        "Certidão de Regularidade Fiscal Federal",
        "não constam débitos em seu nome relativos a tributos federais nem inscrições em dívida ativa da União",
    ),
    DocumentType.CERTIDAO_FGTS: CertificateProfile(
        "Certificado de Regularidade do FGTS - CRF",
        "Prova de Regularidade perante o Fundo de Garantia do Tempo de Serviço",
        "encontra-se em situação regular perante o Fundo de Garantia do Tempo de Serviço (FGTS)",
    ),
    DocumentType.CERTIDAO_TRABALHISTA: CertificateProfile(
        "Certidão Negativa de Débitos Trabalhistas",
        "Certidão Nacional de Débitos Trabalhistas - CNDT",
        "não constam em seu nome débitos trabalhistas inadimplidos",
    ),
}


def certificate_formal_statement(profile: CertificateProfile) -> Layout:
    def layout(slots: Slots, view: ValueFormatter) -> DocumentDraft:
        return draft(
            profile.official_name,
            f"Certifica-se que, em relação a {view.company(slots['supplier_name'], slots['supplier_cnpj'])}, "
            f"{profile.regularity_statement}.",
            f"Certidão emitida em {view.calendar_date(slots['issue_date'])}, com validade até "
            f"{view.calendar_date(slots['valid_until'])}.",
            f"Código de autenticidade: {slots['certificate_code']}.",
        )

    return layout


def certificate_tabular_form(profile: CertificateProfile) -> Layout:
    def layout(slots: Slots, view: ValueFormatter) -> DocumentDraft:
        return draft(
            profile.alternative_name,
            f"DOCUMENTO: {profile.official_name}",
            f"CONTRIBUINTE: {slots['supplier_name']} | {view.cnpj_tag(slots['supplier_cnpj'])}",
            f"DATA DE EMISSÃO: {view.calendar_date(slots['issue_date'])} | "
            f"VÁLIDA ATÉ: {view.calendar_date(slots['valid_until'])}",
            f"CÓDIGO DE CONTROLE: {slots['certificate_code']}",
        )

    return layout


def certificate_validity_first(profile: CertificateProfile) -> Layout:
    def layout(slots: Slots, view: ValueFormatter) -> DocumentDraft:
        return draft(
            profile.alternative_name,
            f"Esta certidão vale até {view.calendar_date(slots['valid_until'])}; foi expedida em "
            f"{view.calendar_date(slots['issue_date'])} sob o código de verificação {slots['certificate_code']}.",
            f"Consta do documento ({profile.official_name}) que, quanto a "
            f"{slots['supplier_name']}, {view.cnpj_tag(slots['supplier_cnpj'])}, {profile.regularity_statement}.",
        )

    return layout


CERTIFICATE_LAYOUTS: LayoutCatalog = {
    document_type: (
        certificate_formal_statement(profile),
        certificate_tabular_form(profile),
        certificate_validity_first(profile),
    )
    for document_type, profile in CERTIFICATE_PROFILES.items()
}
