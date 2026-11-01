PREAMBLE = """Medição em dados **sintéticos**, com gabarito gerado junto do corpus. Estes números não representam o desempenho em processos reais do SEI e não devem ser citados como tal.

Ciclo de 500 processos e 8.844 documentos: 300 de pagamento, 100 de contratação e 100 de prestação de contas, com 11,3% dos documentos como imagem lida por OCR real e 46,6% dos processos com ao menos uma irregularidade semeada. Os números abaixo são os da primeira e única execução: a lógica de análise foi congelada antes de gerar o corpus e nada foi ajustado depois de ver o resultado.

**Taxa de acerto** é a decisão certa por processo. Um processo conta como sinalizado se tiver critério não conforme ou item de conferência humana, então dúvida em processo regular conta como erro. **Conjunto exato** compara os critérios não conformes com os do gabarito. A linha de base "sempre conforme" acerta 53,4%; a comparação honesta é contra ela, não contra zero.

Esta avaliação mede a capacidade de encontrar irregularidades plantadas por um gerador conhecido. Irregularidades reais tendem a ser mais sutis."""

FAMILY_NOTE = """Metade do ciclo usa os modelos de texto com que as regras foram escritas. A outra metade usa uma família inédita, escrita por um agente independente sem acesso às regras nem ao gabarito. Esta é a medida mais próxima de generalização que dados sintéticos permitem.

Sem o modelo de linguagem, as regras caem para 46,8% de acerto e 98,5% de falso alarme no texto inédito. O desempenho acima de 80% depende do modelo: sozinhas, as regras não se sustentam em redação desconhecida, e a variação real do SEI deve ser maior do que a desta família."""

LIMITATIONS = """## 8. Falhas conhecidas

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
- **Integridade.** O gabarito ficou lacrado fora do repositório enquanto o modelo respondia. Nenhuma citação foi rejeitada pela verificação literal, e os subagentes conferiram as próprias citações antes de entregar.
- **Autoria.** O gerador, os critérios e as regras têm a mesma origem. Só a família inédita foi escrita de forma independente, e ela segue o mesmo catálogo de irregularidades.
- **Tempo.** A linha de base de 163,5 minutos é tempo humano disponível por processo. O tempo de máquina não prova redução do trabalho do analista.
- **Integração.** SEI e SINCIN+ são simulados. Nenhum sistema real foi acessado."""
