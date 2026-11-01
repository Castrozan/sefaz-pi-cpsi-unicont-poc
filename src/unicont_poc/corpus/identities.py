from __future__ import annotations

from dataclasses import dataclass
from random import Random

PERSON_FIRST_NAMES = (
    "Abigail",
    "Adriel",
    "Anselmo",
    "Berenice",
    "Caetano",
    "Celina",
    "Damiana",
    "Edvaldo",
    "Elisa",
    "Fabrício",
    "Geraldina",
    "Gervásio",
    "Heloísa",
    "Iracema",
    "Jandira",
    "Juvêncio",
    "Laurinda",
    "Lázaro",
    "Marcelina",
    "Nivaldo",
    "Odete",
    "Otacílio",
    "Perpétua",
    "Quitéria",
    "Raimundo",
    "Rosalina",
    "Sebastiana",
    "Tibério",
    "Ubirajara",
    "Valdete",
    "Zacarias",
    "Zulmira",
)
PERSON_LAST_NAMES = (
    "Albuquerque",
    "Almeida",
    "Araújo",
    "Barros",
    "Bezerra",
    "Brandão",
    "Cardoso",
    "Carvalho",
    "Castelo",
    "Coelho",
    "Correia",
    "Damasceno",
    "Feitosa",
    "Figueiredo",
    "Fontenele",
    "Freitas",
    "Gomes",
    "Holanda",
    "Leal",
    "Lustosa",
    "Macedo",
    "Mendes",
    "Monteiro",
    "Moura",
    "Nogueira",
    "Portela",
    "Rêgo",
    "Sampaio",
    "Soares",
    "Veloso",
)
SUPPLIER_NAMES = (
    "Aroeira Serviços Integrados Ltda",
    "Babaçu Tecnologia e Gestão Ltda",
    "Carnaúba Engenharia e Obras Ltda",
    "Delta Parnaíba Suprimentos Ltda",
    "Estrela do Longá Comércio Ltda",
    "Faveira Soluções Administrativas Ltda",
    "Gameleira Manutenção Predial Ltda",
    "Horizonte do Poti Logística Ltda",
    "Ipê Amarelo Alimentos Ltda",
    "Jatobá Consultoria Pública Ltda",
    "Lagoa Grande Equipamentos Ltda",
    "Mandacaru Saúde e Insumos Ltda",
    "Norte do Canindé Transportes Ltda",
    "Oiticica Informática Ltda",
    "Piaçava Limpeza e Conservação Ltda",
    "Quixabeira Papelaria e Gráfica Ltda",
    "Rio Gurgueia Construções Ltda",
    "Sete Cidades Vigilância Ltda",
    "Tucum Climatização Ltda",
    "Umburana Eventos e Treinamentos Ltda",
)
ORGAN_AREAS = (
    "Saúde",
    "Educação",
    "Infraestrutura",
    "Agricultura Familiar",
    "Assistência Social",
    "Cultura",
    "Turismo",
    "Meio Ambiente",
    "Segurança Cidadã",
    "Administração",
    "Recursos Hídricos",
    "Ciência e Inovação",
    "Trabalho",
    "Esporte",
    "Mulheres",
    "Juventude",
)


@dataclass(frozen=True)
class Organ:
    nucleus_code: str
    name: str
    cnpj: str


def format_cnpj(digits: str) -> str:
    return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:14]}"


def cnpj_check_digits(first_twelve_digits: str) -> str:
    digits = first_twelve_digits
    for weights in ((5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2), (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)):
        remainder = sum(int(digit) * weight for digit, weight in zip(digits, weights)) % 11
        digits += "0" if remainder < 2 else str(11 - remainder)
    return digits[-2:]


def synthetic_cnpj(random_source: Random) -> str:
    root = f"99{random_source.randint(0, 999_999):06d}0001"
    return format_cnpj(root + cnpj_check_digits(root))


def synthetic_process_number(random_source: Random, index: int) -> str:
    return f"9{random_source.randint(1, 56):04d}.{index:06d}/2026-{random_source.randint(0, 99):02d}"


def _build_organs() -> tuple[Organ, ...]:
    random_source = Random(5601)
    return tuple(
        Organ(
            nucleus_code=f"NCI-{number:02d}",
            name=f"Órgão Sintético {number:02d} – {ORGAN_AREAS[(number - 1) % len(ORGAN_AREAS)]}",
            cnpj=synthetic_cnpj(random_source),
        )
        for number in range(1, 57)
    )


ORGANS = _build_organs()
