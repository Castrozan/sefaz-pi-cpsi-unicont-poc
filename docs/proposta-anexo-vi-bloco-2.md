# Rascunho da proposta: Anexo VI, Bloco 2 (Desafio 01, UNICONT)

Rascunho para revisão de Lucas. Nada aqui foi submetido à SEFAZ-PI.

Itens marcados com **[LUCAS]** dependem de informação que só o proponente tem e não foram preenchidos: nenhuma experiência, cliente ou caso foi inventado. Equipe, CPF, CNPJ, declarações e portfólio ficam fora deste rascunho.

## Fundamentação da inovação (art. 13 da LC nº 182/2021 c/c art. 2º, IV, da Lei nº 10.973/2004)

A solução introduz no controle interno do Estado do Piauí um novo processo de análise de conformidade, no sentido do art. 2º, IV, da Lei nº 10.973/2004: agrega a um fluxo hoje integralmente manual a leitura automatizada dos autos, a verificação de critérios e a redação de parecer preliminar, com potencial de ganho de qualidade e desempenho.

O Termo de Referência registra que nenhuma das soluções mapeadas atende à SEFAZ-PI sem adaptação significativa e que não há tentativa anterior estruturada para este problema. A novidade desta proposta está em três características combinadas.

Primeira: um pipeline híbrido, em que regras auditáveis tratam o que é objetivo e um modelo de linguagem trata o que exige leitura, como a compatibilidade entre objeto e despesa ou a ressalva em um atesto.

Segunda: rastreabilidade por construção. Toda conclusão do modelo precisa citar um trecho literal do documento, e o sistema confere essa citação por código. Citação que não confere descarta a conclusão. Cada análise gera um registro encadeado por hashes, com documentos, critérios, resultado, modelo e versão, o que revela alteração de entradas registradas.

Terceira: decisão humana por construção. O sistema redige; o analista decide. O envio ao SINCIN+ é recusado para análise sem aprovação humana registrada.

O risco tecnológico é real e justifica o CPSI: a prova de conceito mostrou que regras escritas para um conjunto de textos perdem desempenho em redação desconhecida, e o comportamento em processos reais do SEI só pode ser medido com os dados anonimizados da Fase 1.

## Descrição do fluxo de funcionamento (pipeline) da solução

1. **Ingestão.** O adaptador do SEI entrega processo e documentos. PDFs com camada de texto são lidos diretamente; PDFs de imagem passam por OCR. Cada documento recebe hash SHA-256.
2. **Indexação (MC-01).** Texto por página e campos extraídos entram em um índice de busca por tipo, campo ou palavra-chave.
3. **Classificação e extração (MC-02).** Regras atribuem tipo documental e extraem valor, CNPJ, número do processo, datas e números de documento. Tipo incerto e campo não lido seguem para o modelo de linguagem.
4. **Leitura pelo modelo (MC-03, MC-04).** O modelo recebe apenas os trechos necessários e devolve resumo, critérios semânticos, tipos e campos, sempre com citação literal, conferida por código.
5. **Verificação (MC-04).** Cada critério do checklist resulta em conforme, não conforme, conferência humana ou prejudicado, com fundamento e evidência citada. Item ilegível vai para o analista, nunca é aprovado por omissão. Os critérios oficiais serão os definidos pela UNICONT.
6. **Pré-triagem (MC-03, MC-05).** Severidade e valor definem risco e prioridade na fila. Repetição de nota fiscal entre processos gera alerta.
7. **Parecer preliminar.** O sistema redige a minuta com resultado, apontamentos e fundamentos.
8. **Decisão do analista.** O analista revisa, edita, aprova ou devolve. Só a aprovação libera o envio ao SINCIN+.
9. **Registro e painel (MC-06).** Análise e decisão entram no registro auditável; o painel consolida indicadores por núcleo, tipo de processo e inconsistência.

A prova de conceito cobre esse fluxo com SEI e SINCIN+ simulados. MC-05 e MC-06 estão em versão inicial.

## Integração com os sistemas e dados da SEFAZ-PI (SEI/SINCIN+, conforme o desafio)

A solução isola SEI e SINCIN+ atrás de duas interfaces: uma recebe processos e documentos, outra devolve o parecer aprovado. A prova de conceito usa implementações simuladas e não acessou nenhum sistema real. A documentação das APIs chega até o Marco P1; com ela, serão escritos os adaptadores reais, e a integração funcional será comprovada até o Marco M1, sem redigitação nem importação manual.

**Dados.** Na Fase 1, apenas dados anonimizados, após assinatura do TCAR. Na Fase 2, dados reais conforme a auditoria de segurança da UNIGEST. Os dados são protegidos por sigilo fiscal (CTN, art. 198) e pela LGPD.

**Portabilidade.** O modelo de linguagem fica atrás de uma interface de um único método, substituível por outro fornecedor ou por modelo hospedado em servidores da SEFAZ-PI, e o pipeline não depende de infraestrutura proprietária da contratada.

**Ponto a definir com a SEFAZ-PI.** O envio de trechos de documentos a um modelo hospedado por terceiro precisa ser aprovado pela UNIGEST antes de qualquer uso com dados internos. Se não for aprovado, a alternativa é um modelo hospedado localmente, cujo desempenho ainda não foi medido nesta prova de conceito.

## Nível de maturidade tecnológica (TRL) atual, autodeclarado

**4**

## TRL projetado ao término do CPSI

**8**, conforme os pisos do Termo de Referência (TRL 5 no Marco M1, 7 no M2 e 8 no M3). É meta condicionada à entrega das APIs, aos dados anonimizados e ao acesso ao ambiente real.

## Justificativa técnica do TRL declarado

O TRL 4 corresponde a componentes integrados e verificados em laboratório. A evidência é um protótipo funcional que percorre todo o fluxo, com relatório de avaliação reproduzível sobre dados sintéticos. O número declarado vale para o núcleo da solução, MC-01 a MC-04, prioridade do Termo de Referência; MC-05 e MC-06 estão em TRL 3, como mostra a tabela. Mesmo no núcleo há fragilidade conhecida: prestação de contas ficou em 72,0%, abaixo da barra de 80%.

O TRL 5 não é declarado porque exige validação em ambiente relevante, e aqui faltam três coisas: dados do SEI, mesmo anonimizados; integração com SEI e SINCIN+; e critérios oficiais da UNICONT. Os adaptadores são simulados, e o modelo de linguagem foi executado em lote, não por API em serviço contínuo.

| # | Microdesafio | Situação na prova de conceito | TRL | Falta para o TRL 5 |
|---|---|---|---|---|
| 1 | MC-01 Busca | Índice sobre 8.844 documentos; mediana de 0,26 ms | 4 | Volume e leiautes reais do SEI |
| 2 | MC-02 Classificação | 99,8% de acerto de tipo em dados sintéticos; depende do modelo em texto inédito | 4 | Tipologias reais e amostra do SEI |
| 3 | MC-03 Resumo e risco | Resumo em 500 de 500 processos; não houve avaliação da qualidade por analistas | 4 | Validação por analistas |
| 4 | MC-04 Conformidade | 94,0% de acerto por processo em dados sintéticos; prestação de contas em 72,0% | 4 | Checklist oficial e gabarito da UNICONT |
| 5 | MC-05 Orquestração | Fila por risco e alerta de duplicidade | 3 | Fluxos reais entre núcleos |
| 6 | MC-06 Painel | Indicadores por núcleo e inconsistência | 3 | Indicadores definidos com a gestão |

Todos os números são de dados sintéticos e não representam desempenho em processos reais.

## Maturidade comercial da solução (existência prévia no mercado e contextos de uso)

A solução é um protótipo desenvolvido para este desafio, sem uso comercial nem implantação em produção comprovados por esta prova de conceito.

**[LUCAS]** Acrescentar existência prévia no mercado e contextos de uso, se houver. Se não houver, manter o parágrafo acima.

## Casos de aplicação ou uso anteriores com tecnologias similares

**[LUCAS]** Descrever casos reais, com evidência. Campo obrigatório: o Termo de Referência (item 5.4.3) exige ao menos um caso ou projeto anterior da equipe. Este rascunho não contém nenhum caso. A prova de conceito não é caso de uso anterior.

## Estimativa de escala, tempestividade e escalabilidade da solução

**Escala.** Foram medidos 500 processos e 8.844 documentos em um ciclo, com dados sintéticos. A etapa sem modelo levou 194 s, com 6 processos paralelos em um computador pessoal, ou 0,39 s por processo.

**Tempestividade.** O tempo de máquina estimado é de 0,19 minuto por processo, somando a mediana de 1,96 s de leitura em série e 9,7 s de modelo por pedido, medidos em lote. A linha de base é de 163,5 minutos de análise humana. Os dois números não são comparáveis diretamente: o analista ainda precisa revisar e decidir, e a redução real do tempo de análise será medida no piloto contra a meta de 50%.

**Escalabilidade.** Os 80.820 processos por ano projetados equivalem a cerca de 306 por dia útil, considerando 22 dias úteis por mês e 12 meses. A leitura em lote é paralelizável. O limite prático está na vazão do modelo de linguagem e nos custos, que ainda não foram medidos em serviço contínuo. A meta de 2.000 processos por mês na Fase 2 está dentro da vazão medida, com a mesma ressalva. A escala para os 56 núcleos depende da capacidade e das regras de acesso do ambiente da SEFAZ-PI.

## Link do vídeo de demonstração (até 5 minutos, válido por, no mínimo, 6 meses)

**[LUCAS]** Publicar o vídeo em local público com validade mínima de 6 meses e colar o link aqui. O arquivo está em `demo/demonstracao.mp4`, e o repositório é privado.
