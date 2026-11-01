from __future__ import annotations

from unicont_poc.corpus.contract import DocumentDraft
from unicont_poc.corpus.families.heldout.layout_support import LayoutCatalog, Slots, draft
from unicont_poc.corpus.families.heldout.presentation import ValueFormatter
from unicont_poc.domain import DocumentType

SUBJECT_ACTIONS = {
    "encaminhamento": (
        "encaminho o processo para prosseguimento",
        "encaminham-se os autos à unidade destinatária para seguimento",
        "segue o processo em encaminhamento para as etapas seguintes",
    ),
    "instrucao": (
        "solicito que o processo seja instruído com a documentação pertinente",
        "determino a instrução do feito com os documentos necessários",
        "requer-se a complementação da instrução processual",
    ),
    "ciencia": (
        "dê-se ciência do teor dos autos",
        "para conhecimento e registro, informa-se o andamento do processo",
        "comunico, para ciência, o andamento do processo",
    ),
    "providencias": (
        "solicito a adoção das providências cabíveis",
        "pede-se que sejam tomadas as providências pertinentes",
        "requer-se atuação para as providências necessárias",
    ),
}


def unrelated_figures(slots: Slots, view: ValueFormatter) -> tuple[str, ...]:
    if slots["unrelated_amount"] is None:
        return ()
    return (
        f"Registra-se, apenas a título informativo, que tramita em separado outro expediente, no valor de "
        f"{view.money(slots['unrelated_amount'])} e relativo à pessoa jurídica de {view.cnpj_tag(slots['unrelated_cnpj'])}, "
        f"sem relação com este processo.",
    )


def dispatch_headed(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    action = SUBJECT_ACTIONS[slots["subject_kind"]][0]
    return draft(
        f"Despacho nº {slots['sequence_number']}",
        f"DESPACHO Nº {slots['sequence_number']} - {view.calendar_date(slots['issue_date'])}.",
        f"Destino: {slots['recipient']}.",
        f"Quanto ao interessado {slots['supplier_name']}, {action}.",
        *unrelated_figures(slots, view),
        f"{slots['signer_name']}, {slots['signer_role']}.",
    )


def dispatch_narrative(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    action = SUBJECT_ACTIONS[slots["subject_kind"]][1]
    return draft(
        "Manifestação nos Autos",
        f"Em {view.calendar_date(slots['issue_date'])}, {slots['signer_name']}, {slots['signer_role']}, lançou nos "
        f"autos o despacho nº {slots['sequence_number']}, com destino a: {slots['recipient']}.",
        f"Teor do despacho, no tocante a {slots['supplier_name']}: {action}.",
        *unrelated_figures(slots, view),
    )


def dispatch_tabular(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    action = SUBJECT_ACTIONS[slots["subject_kind"]][2]
    return draft(
        "Despacho Interno",
        f"DESPACHO | Nº {slots['sequence_number']} | DATA {view.calendar_date(slots['issue_date'])}",
        f"DESTINO | {slots['recipient']} | INTERESSADO | {slots['supplier_name']}",
        f"TEXTO | {action}",
        *unrelated_figures(slots, view),
        f"ASSINA | {slots['signer_name']} | {slots['signer_role']}",
    )


def official_letter_formal(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    action = SUBJECT_ACTIONS[slots["subject_kind"]][0]
    return draft(
        f"Ofício nº {slots['sequence_number']}/{slots['issue_date'].year}",
        f"OFÍCIO Nº {slots['sequence_number']}/{slots['issue_date'].year}, de {view.calendar_date(slots['issue_date'])}.",
        f"Destinatário: {slots['recipient']}.",
        f"Por meio deste ofício, relativo ao interessado {slots['supplier_name']}, {action}.",
        *unrelated_figures(slots, view),
        f"Atenciosamente, {slots['signer_name']}, {slots['signer_role']}.",
    )


def official_letter_narrative(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    action = SUBJECT_ACTIONS[slots["subject_kind"]][1]
    return draft(
        "Comunicação Oficial",
        f"{slots['signer_name']}, {slots['signer_role']}, expediu em {view.calendar_date(slots['issue_date'])} o "
        f"ofício nº {slots['sequence_number']}, dirigido a: {slots['recipient']}.",
        f"Conteúdo, no que se refere a {slots['supplier_name']}: {action}.",
        *unrelated_figures(slots, view),
    )


def official_letter_tabular(slots: Slots, view: ValueFormatter) -> DocumentDraft:
    action = SUBJECT_ACTIONS[slots["subject_kind"]][2]
    return draft(
        "Ofício Externo",
        f"OFÍCIO | Nº {slots['sequence_number']} | EMISSÃO {view.calendar_date(slots['issue_date'])}",
        f"PARA | {slots['recipient']} | ASSUNTO | {slots['supplier_name']}",
        f"MENSAGEM | {action}",
        *unrelated_figures(slots, view),
        f"REMETENTE | {slots['signer_name']} | {slots['signer_role']}",
    )


ROUTINE_LAYOUTS: LayoutCatalog = {
    DocumentType.DESPACHO: (dispatch_headed, dispatch_narrative, dispatch_tabular),
    DocumentType.OFICIO: (official_letter_formal, official_letter_narrative, official_letter_tabular),
}
