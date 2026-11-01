import re
from pathlib import Path

PROPOSAL = Path("docs/proposta-anexo-vi-bloco-2.md").read_text(encoding="utf-8")
ANNEX_FIELD_LIMIT = 2000


def section(heading: str) -> str:
    found = re.search(rf"## {heading}.*?\n\n(.*?)(?=\n## |\Z)", PROPOSAL, re.DOTALL)
    assert found, heading
    return found.group(1).strip()


def test_innovation_rationale_fits_the_annex_limit():
    assert len(section("Fundamentação da inovação")) <= ANNEX_FIELD_LIMIT


def test_every_annex_block_two_field_is_present():
    for heading in (
        "Fundamentação da inovação",
        "Descrição do fluxo",
        "Integração com os sistemas",
        "Nível de maturidade tecnológica",
        "TRL projetado",
        "Justificativa técnica",
        "Maturidade comercial",
        "Casos de aplicação",
        "Estimativa de escala",
        "Link do vídeo",
    ):
        assert section(heading)


def test_declared_trl_stays_within_what_the_evidence_supports():
    assert section("Nível de maturidade tecnológica").strip("*") == "4"


def test_past_claims_are_left_for_the_bidder():
    assert "[LUCAS]" in section("Casos de aplicação")
    assert "[LUCAS]" in section("Link do vídeo")
