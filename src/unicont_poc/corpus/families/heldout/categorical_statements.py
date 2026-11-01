from __future__ import annotations

from unicont_poc.corpus.families.heldout.presentation import unpunctuated

ATTESTATION_STATEMENTS = {
    "sem_ressalva": (
        "o objeto foi recebido integralmente, sem ressalvas",
        "os bens e serviços foram conferidos e aceitos na íntegra, nada havendo a ressalvar",
        "o fornecimento foi recebido por completo, sem observações ou restrições a registrar",
    ),
    "ressalva_execucao": (
        "o objeto foi recebido com ressalva, porque subsiste a seguinte falha de execução, "
        "ainda não sanada pela contratada: {detail}",
        "a execução apresentou falha que continua sem correção, o que se ressalva neste recebimento: {detail}",
        "o fornecimento foi recebido com a ressalva de que permanece pendente a falha de execução a seguir: {detail}",
    ),
    "ressalva_afastada": (
        "houve durante a execução o incidente a seguir, já resolvido pela contratada, razão pela qual "
        "nada há a glosar e o recebimento é integral: {detail}",
        "o objeto foi recebido na íntegra; o incidente registrado, sanado pela contratada e sem glosa "
        "alguma a aplicar, foi este: {detail}",
        "o recebimento é integral e sem desconto algum; consta, a título de histórico, apenas o incidente "
        "já superado: {detail}",
    ),
}

OPINION_CONCLUSIONS = {
    "favoravel": (
        "opinamos favoravelmente ao prosseguimento do feito, sem qualquer condição",
        "não há óbice jurídico à continuidade, sendo o parecer favorável e incondicional",
        "o parecer é favorável, sem condicionantes ou ressalvas",
    ),
    "desfavoravel": (
        "opinamos contrariamente ao prosseguimento, pelo seguinte motivo: {detail}",
        "o parecer é desfavorável, pois o óbice a seguir impede a continuidade: {detail}",
        "não se recomenda o prosseguimento do feito, em razão do seguinte: {detail}",
    ),
    "ressalva_pendente": (
        "o prosseguimento fica condicionado à correção do seguinte ponto, ainda pendente: {detail}",
        "o feito só pode avançar depois de sanado o apontamento a seguir, que permanece em aberto: {detail}",
        "opinamos pelo prosseguimento apenas se for corrigido, antes disso, o ponto pendente: {detail}",
    ),
    "recomendacao_atendida": (
        "o parecer é favorável e a recomendação formulada já foi cumprida, nada mais restando a corrigir: {detail}",
        "opinamos favoravelmente; a recomendação a seguir já foi atendida e não subsiste condição alguma: {detail}",
        "o parecer é favorável e sem pendências, pois já foi cumprida a seguinte recomendação: {detail}",
    ),
}


def attestation_statement(statement_kind: str, exception_detail: str, variant: int) -> str:
    return ATTESTATION_STATEMENTS[statement_kind][variant].format(detail=unpunctuated(exception_detail))


def opinion_conclusion(opinion_kind: str, opinion_detail: str, variant: int) -> str:
    return OPINION_CONCLUSIONS[opinion_kind][variant].format(detail=unpunctuated(opinion_detail))
