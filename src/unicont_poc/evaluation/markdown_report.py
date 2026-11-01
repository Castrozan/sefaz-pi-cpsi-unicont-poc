from __future__ import annotations


def _percent(value: float | None) -> str:
    return "n/d" if value is None else f"{value * 100:.1f}%".replace(".", ",")


def _decimal(value: float) -> str:
    return str(value).replace(".", ",")


def _table(headers: list[str], rows: list[list[object]]) -> str:
    lines = ["| # | " + " | ".join(headers) + " |", "|---|" + "---|" * len(headers)]
    for position, row in enumerate(rows, start=1):
        lines.append(f"| {position} | " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


def _group_rows(groups: dict[str, dict]) -> list[list[object]]:
    return [
        [
            name,
            summary["processos"],
            _percent(summary["taxa_de_acerto_processo"]),
            _percent(summary["acerto_exato_do_conjunto"]),
            _percent(summary["deteccao_em_irregulares"]),
            _percent(summary["falso_alarme_em_regulares"]),
            _percent(summary["com_item_nao_verificavel"]),
        ]
        for name, summary in groups.items()
    ]


GROUP_HEADERS = ["Grupo", "Processos", "Acerto", "Conjunto exato", "Detecção", "Falso alarme", "Com conferência humana"]


def _edital_table(report: dict, wall_minutes_per_process: str) -> str:
    overall = report["global"]
    audit = report["registro_auditavel"]
    rows = [
        ["Escala", "≥ 500 processos por ciclo", f"{overall['processos']} processos", "Atingido em dados sintéticos"],
        ["Precisão", "≥ 80% contra gabarito", _percent(overall["taxa_de_acerto_processo"]), "Ver seções 3 a 5"],
        ["Tempestividade", "Bem abaixo de 163,5 min", wall_minutes_per_process, "Tempo de máquina, não de analista"],
        [
            "Rastreabilidade",
            "100% com registro",
            f"{audit['com_documentos_criterios_resultado_modelo']} de {audit['analises']}",
            f"Cadeia íntegra: {'sim' if audit.get('cadeia_integra') else 'não'}",
        ],
        ["Integração", "Comprovada até M1", "Não demonstrada", "SEI e SINCIN+ simulados; APIs só no Marco P1"],
    ]
    return _table(["Capacidade", "Parâmetro do edital", "Medido", "Observação"], rows)


def render_report(model_report: dict, rules_report: dict, context: dict) -> str:
    documents = model_report["documentos"]
    criteria_rows = [
        [
            f"{row['codigo']} {row['criterio']}{' (semântico)' if row['semantico'] else ''}",
            row["casos_semeados"],
            row["falsos_positivos"],
            row["falsos_negativos"],
            row["nao_verificaveis"],
            _percent(row["precisao"]),
            _percent(row["revocacao"]),
        ]
        for row in model_report["por_criterio"]
    ]
    comparison_rows = [
        [
            label,
            _percent(report["global"]["taxa_de_acerto_processo"]),
            _percent(report["global"]["acerto_exato_do_conjunto"]),
            _percent(report["global"]["deteccao_em_irregulares"]),
            _percent(report["global"]["falso_alarme_em_regulares"]),
            _percent(report["acerto_ponderado_pela_composicao_real"]),
        ]
        for label, report in (
            ("Regras e heurísticas, sem modelo", rules_report),
            ("Regras e modelo de linguagem", model_report),
        )
    ]
    field_rows = [
        [name, documents["campos_avaliados"][name], _percent(rate)]
        for name, rate in documents["extracao_por_campo"].items()
    ]
    origin_rows = [
        [name, documents["documentos_por_origem"][name], _percent(rate)]
        for name, rate in documents["classificacao_por_origem"].items()
    ]
    type_rows = [
        [name, documents["documentos_por_tipo"][name], _percent(rate)]
        for name, rate in sorted(documents["classificacao_por_tipo"].items(), key=lambda item: item[1])
    ]
    confusion_rows = [
        [item["esperado"], item["obtido"], item["casos"]] for item in documents["confusoes_mais_frequentes"]
    ]
    minutes = f"{context['total_minutes_per_process']:.2f} min por processo".replace(".", ",")
    time_section = model_report["tempo"]
    sections = [
        "# Relatório de avaliação da PoC UNICONT",
        context["preamble"],
        "## 1. Resultado frente ao edital\n\n" + _edital_table(model_report, minutes),
        "## 2. Efeito do modelo de linguagem\n\n"
        + _table(
            ["Configuração", "Acerto", "Conjunto exato", "Detecção", "Falso alarme", "Ponderado pela composição real"],
            comparison_rows,
        ),
        "## 3. Por categoria\n\n" + _table(GROUP_HEADERS, _group_rows(model_report["por_categoria"])),
        "## 4. Texto conhecido e texto inédito\n\n"
        + context["family_note"]
        + "\n\n"
        + _table(GROUP_HEADERS, _group_rows(model_report["por_familia_de_template"])),
        "## 5. Por critério, com as falhas\n\n"
        + _table(
            [
                "Critério",
                "Semeados",
                "Falsos positivos",
                "Falsos negativos",
                "Conferência humana",
                "Precisão",
                "Revocação",
            ],
            criteria_rows,
        ),
        "## 6. Classificação e extração de documentos\n\n"
        + f"Classificação global: {_percent(documents['classificacao_global'])}.\n\n"
        + _table(["Origem", "Documentos", "Acerto"], origin_rows)
        + "\n\n"
        + _table(["Campo", "Avaliados", "Acerto"], field_rows)
        + "\n\n### Por tipo de documento\n\n"
        + _table(["Tipo", "Documentos", "Acerto"], type_rows)
        + (
            "\n\n### Confusões mais frequentes\n\n" + _table(["Esperado", "Obtido", "Casos"], confusion_rows)
            if confusion_rows
            else ""
        ),
        "## 7. Tempo\n\n"
        + f"- Leitura, OCR, classificação e regras: {_decimal(time_section['parede_por_processo_segundos'])} s de parede por processo, com {context['workers']} processos paralelos, no ciclo de {_decimal(time_section['parede_do_ciclo_segundos'])} s (replay do modelo).\n"
        + f"- Modelo de linguagem: {str(round(context['language_seconds_per_request'], 1)).replace('.', ',')} s por pedido, medidos no lote sequencial por subagente. É aproximação, não latência de API.\n"
        + f"- Total estimado: {minutes}, somando a mediana de {_decimal(time_section['mediana_por_processo_segundos'])} s de um processo lido em série e o tempo do modelo. A linha de base é de 163,5 min de análise humana.\n"
        + "- A comparação não mede redução do tempo do analista. Isso exige estudo com analistas, previsto para a Fase 2.\n"
        + f"- Busca: mediana de {_decimal(model_report['busca']['mediana_ms'])} ms e máximo de {_decimal(model_report['busca']['maximo_ms'])} ms em {model_report['busca']['consultas']} consultas sobre o ciclo.",
        context["limitations"],
    ]
    return "\n\n".join(sections) + "\n"
