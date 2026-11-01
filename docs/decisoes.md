# Decisões da PoC

Decisões tomadas sem consulta a Lucas, por instrução do briefing, com o motivo de cada uma.

| # | Decisão | Motivo |
|---|---|---|
| 1 | Pipeline híbrido: regras primeiro, modelo de linguagem depois | Regras são auditáveis e baratas; o modelo cobre leitura semântica, tipo incerto e campo não lido |
| 2 | Conclusão do modelo só vale com citação literal, verificada por código | Impede afirmação sem lastro no documento; citação que não confere vira conferência humana |
| 3 | Item ilegível vira conferência humana, nunca "conforme" | Em controle interno, o erro caro é liberar sem ver |
| 4 | Interface `LanguageModel` de um método, com adaptadores Anthropic e replay | Atende à exigência de portabilidade (edital, cláusula 35; ETP, item d) e permite trocar por modelo local |
| 5 | SEI e SINCIN+ atrás de `SeiGateway` e `SincinPlusGateway`, simulados | As APIs só chegam no Marco P1; nenhum sistema real foi acessado |
| 6 | Saída para o SINCIN+ recusa análise sem aprovação humana | A regra está no adaptador, não na tela |
| 7 | Livro de auditoria com cadeia de hashes em SQLite | Padrão simples, sem dependência externa; alteração de entrada registrada é detectável, remoção das últimas entradas não |
| 8 | PDF real por documento e OCR real com Tesseract em cerca de 11% deles | Erros de OCR autênticos valem mais que ruído simulado |
| 9 | Família de texto inédita, escrita por agente independente sem acesso às regras nem ao gabarito | O autor das regras não pode ser o autor de todo o teste; é a medida de generalização |
| 10 | Conjunto de desenvolvimento com semente própria; lógica de decisão congelada no commit `97febfe` antes de gerar a avaliação; medição executada no `0f25ab1`, que só muda o recorte das citações exibidas | Evita ajustar regras olhando o teste |
| 11 | Gabarito lacrado fora do repositório enquanto o modelo respondia | O modelo não pode ter contato com a resposta |
| 12 | Composição 300/100/100 no ciclo, com resultado também ponderado pela composição real (88,2/6,3/5,5) | Com a composição real haveria só 31 contratações e 28 prestações, poucas para medir por critério |
| 13 | Taxa de 45% de processos com irregularidade | Mantém a linha de base "sempre conforme" longe do alvo; a taxa real é desconhecida |
| 14 | Item não verificável conta como processo sinalizado na taxa de acerto | Não esconde dúvida do sistema: em processo regular, conta como erro |
| 15 | Critérios ilustrativos derivados de normas públicas | O checklist oficial é da UNICONT e não é público |
| 16 | Nada de `claude -p` | Bloqueado neste ambiente, e não há `ANTHROPIC_API_KEY`; a sentinela é para exceção sancionada, que ninguém concedeu |
| 17 | Respostas geradas por subagentes Claude em lotes e reproduzidas por replay | É o caminho autorizado; latência e isolamento diferem de chamadas de API, e o relatório declara isso |
| 18 | CNPJ com raiz iniciada em 99 e dígitos válidos; órgãos "Órgão Sintético NN" | Item 35 do edital; colisão com CNPJ real é improvável, mas não impossível |
| 19 | Correções depois da medição limitadas a texto, fundamentos, livro de auditoria e validação de aprovação | Nenhuma altera decisão de critério; o replay confirma os mesmos números |
| 20 | Legendas embutidas no vídeo, sem narração | Geração de voz não tem orçamento autorizado |
| 21 | Site público exportado dos mesmos templates, com rotas trocadas por `StaticRoutes`, em vez de uma segunda interface em JavaScript | Tela e números têm uma única origem; a exportação só lê `dados/` |
| 22 | Busca do site com SQLite em WebAssembly sobre o índice FTS5 exportado | Mesmo índice, tokenizador e consulta do servidor; o teste compara os resultados com a busca em Python |
| 23 | Decisões do site guardadas em `localStorage`, com protocolo `SIMULADO-` e cadeia de hashes local | Site estático não tem servidor; a regra de recusa é a mesma, e nada sai do navegador |
| 24 | PDFs originais fora do site; o link aponta para o corpus da versão `avaliacao-1` | São 94 MB fora do escopo pedido; o texto de cada documento está no site |
