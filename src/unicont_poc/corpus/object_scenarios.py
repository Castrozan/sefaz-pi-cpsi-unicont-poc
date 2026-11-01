from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ObjectScenario:
    object_text: str
    need_text: str
    invoice_descriptions: tuple[str, ...]
    incompatible_invoice_descriptions: tuple[str, ...]
    execution_exceptions: tuple[str, ...]
    resolved_exceptions: tuple[str, ...]
    legal_objections: tuple[str, ...]
    resolved_legal_recommendations: tuple[str, ...]
    divergent_object_texts: tuple[str, ...]
    requires_technical_responsibility: bool = False


COMMON_LEGAL_OBJECTIONS = (
    "ausência de justificativa para a vedação à participação de consórcios, ponto que precisa ser sanado antes da assinatura",
    "matriz de riscos incompleta, devendo o processo retornar à unidade demandante para complementação",
    "exigência de habilitação técnica sem amparo legal, recomendando-se a não continuidade até a correção",
)
COMMON_RESOLVED_RECOMMENDATIONS = (
    "ajuste na redação da cláusula de reajuste, já incorporado à minuta conforme despacho posterior da área técnica",
    "inclusão da designação do gestor, providência já cumprida na versão final da minuta",
)

OBJECT_SCENARIOS: tuple[ObjectScenario, ...] = (
    ObjectScenario(
        "prestação de serviços continuados de limpeza e conservação predial nas unidades administrativas",
        "as unidades administrativas não dispõem de pessoal próprio para limpeza e conservação dos prédios",
        (
            "serviços de limpeza predial",
            "serviços de conservação e higienização de ambientes",
            "fornecimento de material de limpeza para os serviços",
        ),
        (
            "locação de sonorização e palco para evento festivo",
            "buffet para coquetel de confraternização",
            "aquisição de notebooks e tablets",
        ),
        (
            "as equipes compareceram em apenas 12 dos 22 dias previstos e os sanitários do bloco B não foram higienizados",
            "o serviço foi executado parcialmente, faltando a conservação das áreas externas no período",
        ),
        (
            "foi apontada falta de sabão no dia 3, porém o item foi reposto no dia seguinte e o serviço foi integralmente prestado",
        ),
        COMMON_LEGAL_OBJECTIONS,
        COMMON_RESOLVED_RECOMMENDATIONS,
        (
            "fornecimento de refeições prontas para eventos institucionais",
            "aquisição de veículos utilitários para a frota",
        ),
    ),
    ObjectScenario(
        "fornecimento de medicamentos e insumos hospitalares para a rede estadual de saúde",
        "há desabastecimento recorrente de medicamentos e insumos na rede estadual",
        (
            "medicamentos da lista básica",
            "seringas, luvas e insumos hospitalares",
            "soro fisiológico e material de curativo",
        ),
        (
            "pintura de fachada e reparos em telhado",
            "manutenção de ar condicionado de gabinete",
            "assinatura de software de edição de vídeo",
        ),
        (
            "foram entregues apenas 60% das caixas previstas e 200 unidades estavam com a validade vencida",
            "parte do lote chegou avariada e não foi recebida pela farmácia central",
        ),
        (
            "uma caixa foi entregue com embalagem danificada, mas foi substituída pelo fornecedor antes do recebimento definitivo",
        ),
        COMMON_LEGAL_OBJECTIONS,
        COMMON_RESOLVED_RECOMMENDATIONS,
        (
            "reforma das instalações físicas da farmácia central",
            "contratação de consultoria em marketing institucional",
        ),
    ),
    ObjectScenario(
        "execução de obra de reforma e ampliação de escola da rede estadual",
        "a escola opera com salas superlotadas e estrutura comprometida",
        (
            "medição de obra de reforma da escola",
            "serviços de alvenaria e cobertura da escola",
            "execução de instalações elétricas da ampliação",
        ),
        (
            "aquisição de gêneros alimentícios para merenda",
            "serviço de publicidade em rádio",
            "locação de veículos executivos",
        ),
        (
            "a cobertura do pavilhão 2 foi medida, mas não foi executada, conforme vistoria do dia 14",
            "foram constatadas infiltrações e a etapa não pode ser considerada concluída",
        ),
        ("houve atraso pontual na entrega de telhas, sanado dentro do cronograma da medição",),
        COMMON_LEGAL_OBJECTIONS,
        COMMON_RESOLVED_RECOMMENDATIONS,
        ("aquisição de mobiliário escolar e material didático", "serviço de transporte escolar terceirizado"),
        True,
    ),
    ObjectScenario(
        "locação de veículos com motorista para apoio às atividades de fiscalização",
        "as equipes de fiscalização não dispõem de frota suficiente para atender ao interior do Estado",
        (
            "locação mensal de veículos com motorista",
            "diárias de veículo para fiscalização",
            "quilometragem excedente de veículos locados",
        ),
        ("aquisição de cestas básicas", "reforma de banheiros do prédio-sede", "impressão de banners e panfletos"),
        (
            "dois veículos permaneceram indisponíveis por 9 dias e não houve substituição",
            "a frota entregue foi inferior à contratada durante todo o mês",
        ),
        ("um veículo ficou parado por meio dia para troca de pneu e foi substituído sem prejuízo à fiscalização",),
        COMMON_LEGAL_OBJECTIONS,
        COMMON_RESOLVED_RECOMMENDATIONS,
        ("aquisição de motocicletas para a frota própria", "serviço de manutenção de geradores"),
    ),
    ObjectScenario(
        "suporte técnico e manutenção de sistemas de informação corporativos",
        "os sistemas corporativos precisam de suporte especializado que a equipe interna não oferece",
        (
            "horas de suporte técnico a sistemas",
            "manutenção corretiva e evolutiva de sistemas",
            "sustentação de ambiente de sistemas corporativos",
        ),
        ("fornecimento de refeições para servidores", "aquisição de fardamento", "obra de drenagem em estacionamento"),
        (
            "os chamados críticos ficaram sem atendimento por 11 dias e o relatório de níveis de serviço não foi entregue",
            "apenas 40% das horas faturadas têm registro no sistema de chamados",
        ),
        ("um chamado foi reaberto, mas foi resolvido dentro do prazo do acordo de nível de serviço",),
        COMMON_LEGAL_OBJECTIONS,
        COMMON_RESOLVED_RECOMMENDATIONS,
        (
            "aquisição de licenças perpétuas e equipamentos de datacenter",
            "treinamento presencial de servidores em oratória",
        ),
    ),
    ObjectScenario(
        "fornecimento de refeições para unidades de atendimento à população",
        "as unidades de atendimento funcionam em tempo integral e precisam de alimentação para os assistidos",
        (
            "refeições prontas tipo marmita",
            "café da manhã e lanches para assistidos",
            "gêneros alimentícios preparados",
        ),
        ("serviços de engenharia elétrica", "aquisição de pneus para a frota", "consultoria tributária"),
        (
            "foram servidas 1.200 refeições a menos do que as faturadas no período",
            "a vigilância sanitária interditou a cozinha por 6 dias e não houve fornecimento",
        ),
        ("a entrega do dia 8 atrasou 30 minutos, sem falta de refeições aos assistidos",),
        COMMON_LEGAL_OBJECTIONS,
        COMMON_RESOLVED_RECOMMENDATIONS,
        ("reforma da cozinha industrial da unidade", "aquisição de veículo refrigerado"),
    ),
)
