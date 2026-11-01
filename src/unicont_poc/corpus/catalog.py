from __future__ import annotations

from dataclasses import dataclass

from unicont_poc.domain import ProcessCategory


@dataclass(frozen=True)
class ChecklistItem:
    code: str
    category: ProcessCategory
    title: str
    legal_basis: str
    is_semantic: bool = False


_PAGAMENTO = ProcessCategory.PAGAMENTO
_CONTRATACAO = ProcessCategory.CONTRATACAO
_PRESTACAO = ProcessCategory.PRESTACAO_DE_CONTAS
CONVENIO_RULE = "Termo do convênio; norma estadual a confirmar com a UNICONT"

CHECKLIST: tuple[ChecklistItem, ...] = (
    ChecklistItem("PAG-01", _PAGAMENTO, "Nota fiscal anexada", "Lei 4.320/1964, art. 63, § 2º, III"),
    ChecklistItem("PAG-02", _PAGAMENTO, "Atesto de recebimento anexado", "Lei 4.320/1964, art. 63, § 2º, III"),
    ChecklistItem("PAG-03", _PAGAMENTO, "Certidões de regularidade anexadas", "Lei 14.133/2021, arts. 68 e 92, XVI"),
    ChecklistItem(
        "PAG-04", _PAGAMENTO, "Certidões válidas na data do pagamento", "Lei 14.133/2021, arts. 68 e 92, XVI"
    ),
    ChecklistItem(
        "PAG-05", _PAGAMENTO, "Valor pago igual ao valor das notas fiscais", "Lei 4.320/1964, art. 63, § 1º, II"
    ),
    ChecklistItem("PAG-06", _PAGAMENTO, "Valor pago coberto pelo empenho", "Lei 4.320/1964, art. 63, § 2º, II"),
    ChecklistItem(
        "PAG-07", _PAGAMENTO, "CNPJ da nota fiscal igual ao do contrato", "Lei 4.320/1964, art. 63, § 1º, III"
    ),
    ChecklistItem("PAG-08", _PAGAMENTO, "Empenho anterior à despesa", "Lei 4.320/1964, art. 60"),
    ChecklistItem("PAG-09", _PAGAMENTO, "Nota fiscal sem duplicidade em outro processo", "Lei 4.320/1964, art. 63"),
    ChecklistItem(
        "PAG-10",
        _PAGAMENTO,
        "Objeto da nota fiscal compatível com o contrato",
        "Lei 4.320/1964, art. 63, § 2º, I",
        True,
    ),
    ChecklistItem("PAG-11", _PAGAMENTO, "Atesto sem ressalva sobre a execução", "Lei 14.133/2021, art. 117", True),
    ChecklistItem("CON-01", _CONTRATACAO, "Estudo técnico preliminar anexado", "Lei 14.133/2021, art. 18, I"),
    ChecklistItem("CON-02", _CONTRATACAO, "Termo de referência anexado", "Lei 14.133/2021, art. 18, II"),
    ChecklistItem("CON-03", _CONTRATACAO, "Parecer jurídico anexado", "Lei 14.133/2021, art. 53"),
    ChecklistItem(
        "CON-04",
        _CONTRATACAO,
        "Pesquisa de preços com ao menos 3 fornecedores",
        "Lei 14.133/2021, art. 23, § 1º, IV, quando for pesquisa direta",
    ),
    ChecklistItem("CON-05", _CONTRATACAO, "Valor contratado dentro do valor estimado", "Lei 14.133/2021, art. 11, III"),
    ChecklistItem("CON-06", _CONTRATACAO, "Fiscal do contrato designado", "Lei 14.133/2021, art. 117"),
    ChecklistItem("CON-07", _CONTRATACAO, "CNPJ da proposta igual ao do contrato", "Lei 14.133/2021, art. 92, II"),
    ChecklistItem(
        "CON-08", _CONTRATACAO, "Parecer jurídico favorável, sem ressalva pendente", "Lei 14.133/2021, art. 53", True
    ),
    ChecklistItem(
        "CON-09",
        _CONTRATACAO,
        "Objeto do contrato aderente ao termo de referência",
        "Lei 14.133/2021, art. 92, I",
        True,
    ),
    ChecklistItem("PRE-01", _PRESTACAO, "Relatório de execução anexado", "CF/1988, art. 70, parágrafo único"),
    ChecklistItem("PRE-02", _PRESTACAO, "Extrato bancário anexado", "CF/1988, art. 70, parágrafo único"),
    ChecklistItem("PRE-03", _PRESTACAO, "Saldo remanescente devolvido", CONVENIO_RULE),
    ChecklistItem(
        "PRE-04", _PRESTACAO, "Soma das despesas igual ao total declarado", "CF/1988, art. 70, parágrafo único"
    ),
    ChecklistItem("PRE-05", _PRESTACAO, "Despesas dentro da vigência do convênio", CONVENIO_RULE),
    ChecklistItem("PRE-06", _PRESTACAO, "Prestação de contas entregue no prazo", "CF/1988, art. 70, parágrafo único"),
    ChecklistItem("PRE-07", _PRESTACAO, "Despesas compatíveis com o plano de trabalho", CONVENIO_RULE, True),
)

CHECKLIST_BY_CODE = {item.code: item for item in CHECKLIST}


def checklist_for(category: ProcessCategory) -> tuple[ChecklistItem, ...]:
    return tuple(item for item in CHECKLIST if item.category is category)
