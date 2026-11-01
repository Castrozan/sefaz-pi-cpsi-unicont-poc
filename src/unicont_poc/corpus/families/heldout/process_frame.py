from __future__ import annotations

from random import Random

from unicont_poc.corpus.families.heldout.layout_support import Slots
from unicont_poc.corpus.families.heldout.presentation import ValueFormatter

FRAME_TEMPLATES = (
    "Processo administrativo nº {process_number} - {organ_name}, {organ_tag}. Documento SEI nº {sei_number}.",
    "Documento SEI nº {sei_number}, juntado aos autos do processo {process_number} ({organ_name}, {organ_tag}).",
    "Autos nº {process_number} | {organ_name} | {organ_tag} | SEI {sei_number}",
    "Unidade: {organ_name} ({organ_tag}). Referência: processo {process_number}; SEI {sei_number}.",
)


def process_frame(slots: Slots, view: ValueFormatter, random_source: Random) -> str:
    return random_source.choice(FRAME_TEMPLATES).format(
        process_number=slots["process_number"],
        organ_name=slots["organ_name"],
        organ_tag=view.cnpj_tag(slots["organ_cnpj"]),
        sei_number=slots["sei_number"],
    )
