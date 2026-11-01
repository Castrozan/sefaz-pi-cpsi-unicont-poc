from __future__ import annotations

from random import Random
from typing import Any

from unicont_poc.corpus.contract import DocumentDraft
from unicont_poc.corpus.formatting import brazilian_money, long_date, numeric_date
from unicont_poc.domain import DocumentType

SUBJECT_SENTENCES = {
    "encaminhamento": "Encaminhamos os autos para conhecimento e prosseguimento do feito.",
    "instrucao": "Solicitamos a devida instrução dos autos, com a juntada dos documentos pertinentes.",
    "ciencia": "Damos ciência às unidades envolvidas para acompanhamento.",
    "providencias": "Solicitamos as providências cabíveis no âmbito de suas atribuições.",
}


def _unrelated_mention(slots: dict[str, Any]) -> list[str]:
    if slots["unrelated_amount"] is None:
        return []
    return [
        f"Registre-se, apenas para fins de histórico, o montante global de {brazilian_money(slots['unrelated_amount'])} "
        f"da unidade no exercício, e a consulta cadastral do CNPJ {slots['unrelated_cnpj']}."
    ]


def render_dispatch(slots: dict[str, Any], random_source: Random) -> DocumentDraft:
    return DocumentDraft(
        f"DESPACHO Nº {slots['sequence_number']}/2026",
        (
            f"Processo nº {slots['process_number']}",
            f"À {slots['recipient']}.",
            SUBJECT_SENTENCES[slots["subject_kind"]],
            *_unrelated_mention(slots),
            f"Teresina, {long_date(slots['issue_date'])}.",
            f"{slots['signer_name']} – {slots['signer_role']}",
        ),
    )


def render_official_letter(slots: dict[str, Any], random_source: Random) -> DocumentDraft:
    return DocumentDraft(
        f"OFÍCIO Nº {slots['sequence_number'] + 100}/2026",
        (
            f"Teresina, {numeric_date(slots['issue_date'])}.",
            f"Ao(À) {slots['recipient']}",
            f"Assunto: Processo SEI {slots['process_number']} – {slots['supplier_name']}.",
            SUBJECT_SENTENCES[slots["subject_kind"]],
            *_unrelated_mention(slots),
            "Atenciosamente,",
            f"{slots['signer_name']}, {slots['signer_role']}.",
        ),
    )


ROUTINE_RENDERERS = {DocumentType.DESPACHO: render_dispatch, DocumentType.OFICIO: render_official_letter}
