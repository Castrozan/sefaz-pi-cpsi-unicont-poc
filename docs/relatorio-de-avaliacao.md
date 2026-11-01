# Relatório de avaliação da PoC UNICONT

Medição em dados **sintéticos**, com gabarito gerado junto do corpus. Estes números não representam o desempenho em processos reais do SEI e não devem ser citados como tal.

Ciclo de 500 processos e 8.844 documentos: 300 de pagamento, 100 de contratação e 100 de prestação de contas, com 11,3% dos documentos como imagem lida por OCR real e 46,6% dos processos com ao menos uma irregularidade semeada. Os números abaixo são os da primeira execução: a lógica de decisão foi congelada no commit `97febfe`, antes de gerar o corpus, e a medição rodou no `0f25ab1`, que só muda o recorte das citações exibidas. Depois de ver o resultado, nenhuma regra, prompt ou limiar foi ajustado.

**Taxa de acerto** é a decisão certa por processo. Um processo conta como sinalizado se tiver critério não conforme ou item de conferência humana, então dúvida em processo regular conta como erro. **Conjunto exato** compara os critérios não conformes com os do gabarito. A linha de base "sempre conforme" acerta 53,4%; a comparação honesta é contra ela, não contra zero.

Esta avaliação mede a capacidade de encontrar irregularidades plantadas por um gerador conhecido. Irregularidades reais tendem a ser mais sutis.

## 1. Resultado frente ao edital

| # | Capacidade | Parâmetro do edital | Medido | Observação |
|---|---|---|---|---|
| 1 | Escala | ≥ 500 processos por ciclo | 500 processos | Atingido em dados sintéticos |
| 2 | Precisão | ≥ 80% contra gabarito | 94,0% | Ver seções 3 a 5 |
| 3 | Tempestividade | Bem abaixo de 163,5 min | 0,19 min por processo | Tempo de máquina, não de analista |
| 4 | Rastreabilidade | 100% com registro | 500 de 500 | Cadeia íntegra: sim |
| 5 | Integração | Comprovada até M1 | Não demonstrada | SEI e SINCIN+ simulados; APIs só no Marco P1 |

## 2. Efeito do modelo de linguagem

| # | Configuração | Acerto | Conjunto exato | Detecção | Falso alarme | Ponderado pela composição real |
|---|---|---|---|---|---|---|
| 1 | Regras e heurísticas, sem modelo | 71,4% | 57,8% | 99,1% | 52,8% | 71,6% |
| 2 | Regras e modelo de linguagem | 94,0% | 95,0% | 99,1% | 10,5% | 97,8% |

## 3. Por categoria

| # | Grupo | Processos | Acerto | Conjunto exato | Detecção | Falso alarme | Com conferência humana |
|---|---|---|---|---|---|---|---|
| 1 | pagamento | 300 | 99,3% | 99,0% | 98,5% | 0,0% | 9,3% |
| 2 | prestacao_de_contas | 100 | 72,0% | 78,0% | 100,0% | 49,1% | 30,0% |
| 3 | contratacao | 100 | 100,0% | 100,0% | 100,0% | 0,0% | 17,0% |

## 4. Texto conhecido e texto inédito

Metade do ciclo usa os modelos de texto com que as regras foram escritas. A outra metade usa uma família inédita, escrita por um agente independente sem acesso às regras nem ao gabarito. Esta é a medida mais próxima de generalização que dados sintéticos permitem.

Sem o modelo de linguagem, as regras caem para 46,8% de acerto e 98,5% de falso alarme no texto inédito. O desempenho acima de 80% depende do modelo: sozinhas, as regras não se sustentam em redação desconhecida, e a variação real do SEI deve ser maior do que a desta família.

| # | Grupo | Processos | Acerto | Conjunto exato | Detecção | Falso alarme | Com conferência humana |
|---|---|---|---|---|---|---|---|
| 1 | inedita | 250 | 90,4% | 91,2% | 100,0% | 17,9% | 21,6% |
| 2 | padrao | 250 | 97,6% | 98,8% | 98,3% | 3,0% | 8,4% |

## 5. Por critério, com as falhas

| # | Critério | Semeados | Falsos positivos | Falsos negativos | Conferência humana | Precisão | Revocação |
|---|---|---|---|---|---|---|---|
| 1 | PAG-01 Nota fiscal anexada | 7 | 0 | 0 | 0 | 100,0% | 100,0% |
| 2 | PAG-02 Atesto de recebimento anexado | 20 | 0 | 0 | 0 | 100,0% | 100,0% |
| 3 | PAG-03 Certidões de regularidade anexadas | 27 | 0 | 0 | 0 | 100,0% | 100,0% |
| 4 | PAG-04 Certidões válidas na data do pagamento | 21 | 0 | 0 | 0 | 100,0% | 100,0% |
| 5 | PAG-05 Valor pago igual ao valor das notas fiscais | 17 | 0 | 0 | 0 | 100,0% | 100,0% |
| 6 | PAG-06 Valor pago coberto pelo empenho | 22 | 0 | 1 | 0 | 100,0% | 95,5% |
| 7 | PAG-07 CNPJ da nota fiscal igual ao do contrato | 13 | 0 | 0 | 0 | 100,0% | 100,0% |
| 8 | PAG-08 Empenho anterior à despesa | 10 | 0 | 0 | 0 | 100,0% | 100,0% |
| 9 | PAG-09 Nota fiscal sem duplicidade em outro processo | 16 | 0 | 2 | 0 | 100,0% | 87,5% |
| 10 | PAG-10 Objeto da nota fiscal compatível com o contrato (semântico) | 21 | 0 | 0 | 7 | 100,0% | 100,0% |
| 11 | PAG-11 Atesto sem ressalva sobre a execução (semântico) | 28 | 0 | 0 | 22 | 100,0% | 100,0% |
| 12 | CON-01 Estudo técnico preliminar anexado | 9 | 0 | 0 | 0 | 100,0% | 100,0% |
| 13 | CON-02 Termo de referência anexado | 12 | 0 | 0 | 0 | 100,0% | 100,0% |
| 14 | CON-03 Parecer jurídico anexado | 6 | 0 | 0 | 0 | 100,0% | 100,0% |
| 15 | CON-04 Pesquisa de preços com ao menos 3 fornecedores | 5 | 0 | 0 | 0 | 100,0% | 100,0% |
| 16 | CON-05 Valor contratado dentro do valor estimado | 8 | 0 | 0 | 0 | 100,0% | 100,0% |
| 17 | CON-06 Fiscal do contrato designado | 6 | 0 | 0 | 0 | 100,0% | 100,0% |
| 18 | CON-07 CNPJ da proposta igual ao do contrato | 7 | 0 | 0 | 0 | 100,0% | 100,0% |
| 19 | CON-08 Parecer jurídico favorável, sem ressalva pendente (semântico) | 12 | 0 | 0 | 6 | 100,0% | 100,0% |
| 20 | CON-09 Objeto do contrato aderente ao termo de referência (semântico) | 6 | 0 | 0 | 12 | 100,0% | 100,0% |
| 21 | PRE-01 Relatório de execução anexado | 10 | 0 | 0 | 0 | 100,0% | 100,0% |
| 22 | PRE-02 Extrato bancário anexado | 5 | 2 | 0 | 0 | 71,4% | 100,0% |
| 23 | PRE-03 Saldo remanescente devolvido | 10 | 0 | 0 | 0 | 100,0% | 100,0% |
| 24 | PRE-04 Soma das despesas igual ao total declarado | 11 | 17 | 1 | 17 | 37,0% | 90,9% |
| 25 | PRE-05 Despesas dentro da vigência do convênio | 7 | 0 | 0 | 1 | 100,0% | 100,0% |
| 26 | PRE-06 Prestação de contas entregue no prazo | 9 | 0 | 0 | 4 | 100,0% | 100,0% |
| 27 | PRE-07 Despesas compatíveis com o plano de trabalho (semântico) | 11 | 0 | 2 | 21 | 100,0% | 81,8% |

## 6. Classificação e extração de documentos

Classificação global: 99,8%.

| # | Origem | Documentos | Acerto |
|---|---|---|---|
| 1 | digitalizado | 999 | 99,4% |
| 2 | texto_nativo | 7845 | 99,9% |

| # | Campo | Avaliados | Acerto |
|---|---|---|---|
| 1 | amount | 2449 | 99,2% |
| 2 | cnpj | 3030 | 98,6% |
| 3 | process_number | 8355 | 99,8% |

### Por tipo de documento

| # | Tipo | Documentos | Acerto |
|---|---|---|---|
| 1 | liquidacao | 300 | 96,0% |
| 2 | extrato_bancario | 95 | 97,9% |
| 3 | comprovante_devolucao | 67 | 98,5% |
| 4 | relacao_pagamentos | 100 | 99,0% |
| 5 | art | 18 | 100,0% |
| 6 | atesto | 280 | 100,0% |
| 7 | certidao_federal | 302 | 100,0% |
| 8 | certidao_fgts | 319 | 100,0% |
| 9 | certidao_trabalhista | 316 | 100,0% |
| 10 | contrato | 400 | 100,0% |
| 11 | despacho | 2350 | 100,0% |
| 12 | estudo_tecnico_preliminar | 91 | 100,0% |
| 13 | nota_empenho | 342 | 100,0% |
| 14 | nota_fiscal | 361 | 100,0% |
| 15 | oficio | 2437 | 100,0% |
| 16 | ordem_pagamento | 300 | 100,0% |
| 17 | parecer_juridico | 94 | 100,0% |
| 18 | pesquisa_precos | 100 | 100,0% |
| 19 | plano_trabalho | 100 | 100,0% |
| 20 | portaria_fiscal | 94 | 100,0% |
| 21 | proposta | 100 | 100,0% |
| 22 | relatorio_execucao | 90 | 100,0% |
| 23 | termo_convenio | 100 | 100,0% |
| 24 | termo_referencia | 88 | 100,0% |

### Confusões mais frequentes

| # | Esperado | Obtido | Casos |
|---|---|---|---|
| 1 | liquidacao | nota_empenho | 12 |
| 2 | extrato_bancario | termo_convenio | 2 |
| 3 | relacao_pagamentos | termo_convenio | 1 |
| 4 | comprovante_devolucao | termo_convenio | 1 |

## 7. Tempo

- Leitura, OCR, classificação e regras: 0,388 s de parede por processo, com 6 processos paralelos, no ciclo de 194,0 s (replay do modelo).
- Modelo de linguagem: 9,7 s por pedido, medidos no lote sequencial por subagente. É aproximação, não latência de API.
- Total estimado: 0,19 min por processo, somando a mediana de 1,96 s de um processo lido em série e o tempo do modelo. A linha de base é de 163,5 min de análise humana.
- A comparação não mede redução do tempo do analista. Isso exige estudo com analistas, previsto para a Fase 2.
- Busca: mediana de 0,26 ms e máximo de 1,57 ms em 80 consultas sobre o ciclo.

## 8. Falhas conhecidas

Causas identificadas depois da medição. Não foram corrigidas, para que o código entregue seja o código medido.

| # | Falha | Efeito medido | Causa |
|---|---|---|---|
| 1 | Prestação de contas abaixo da barra | 72,0% de acerto, 49,1% de falso alarme | Falhas 2 e 3 |
| 2 | Soma de despesas em leiaute desconhecido | PRE-04: 17 falsos positivos e 17 itens de conferência humana | Linhas não lidas viram soma parcial, que diverge do total e gera falso alarme; deveria virar conferência humana |
| 3 | Relação de despesas truncada para o modelo | PRE-07: 19 itens de conferência humana e 2 irregularidades não confirmadas | O trecho enviado ao modelo tem 1.000 caracteres, menos que a relação completa |
| 4 | Duplicidade de nota fiscal não detectada | PAG-09: 2 de 16 perdidas, os 2 únicos processos irregulares liberados sem nenhum alerta | Na nota original, em texto inédito, o extrator leu o número do documento SEI no lugar do número da nota, e a repetição não casou |
| 5 | Liquidação classificada como empenho | 12 documentos; PAG-06: 1 irregularidade perdida | Regra de alta confiança não vai ao modelo; o valor da liquidação somou ao empenhado |
| 6 | Critério semântico sem documento-base | 15,0% dos processos têm item de conferência humana; parte vem daqui | O modelo devolve "não verificável" onde o certo é "prejudicado" |

A falha 4 é a mais grave: é o único caso em que um processo irregular saiu sem alerta. O sistema não substitui a leitura do analista.

## 9. Limites desta medição

- **Dados.** Sintéticos, com irregularidades plantadas e taxa de 46,6% arbitrada. A taxa real é desconhecida.
- **Critérios.** Ilustrativos, derivados de normas públicas. O checklist oficial é da UNICONT e pode mudar o resultado.
- **Modelo.** `claude-sonnet-5-5`, em 14 lotes sequenciais de subagentes do Claude Code, por falta de chave de API no ambiente. Os pedidos de um lote compartilham contexto, o que não ocorre em chamadas de API independentes. O adaptador de API está implementado e testado contra cliente simulado, sem nenhuma chamada real.
- **Integridade.** O gabarito ficou lacrado fora do repositório enquanto o modelo respondia. Nenhuma citação foi rejeitada pela verificação literal, e os subagentes conferiram as próprias citações antes de entregar. A verificação prova que o trecho existe no documento, não que ele sustenta a conclusão: quem julga isso é o analista.
- **Auditoria.** A cadeia de hashes revela alteração de entradas registradas, mas não a remoção das últimas entradas. Isso exige publicar o hash final em local externo. O nome do analista é texto livre: a PoC não tem autenticação.
- **Autoria.** O gerador, os critérios e as regras têm a mesma origem. Só a família inédita foi escrita de forma independente, e ela segue o mesmo catálogo de irregularidades.
- **Tempo.** A linha de base de 163,5 minutos é tempo humano disponível por processo. O tempo de máquina não prova redução do trabalho do analista. As durações dos lotes estão em `dados/tempos-dos-lotes.json`.
- **Integração.** SEI e SINCIN+ são simulados. Nenhum sistema real foi acessado.
