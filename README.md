# Assistente de conformidade para os Núcleos de Controle Interno

Prova de conceito para o Desafio 01 (UNICONT) do CPSI 001/2026 da SEFAZ-PI. O sistema analisa processos, verifica critérios com evidência citada do documento e redige um parecer preliminar. Quem decide é o analista.

Usa somente dados sintéticos, conforme o item 35 do edital: nomes e números foram inventados, e coincidência com nome ou CNPJ real é acidental. Nenhum sistema da SEFAZ-PI foi acessado.

## Demonstração pública

[Abrir a demonstração no navegador](https://castrozan.github.io/sefaz-pi-cpsi-unicont-poc/). É uma exportação estática do estado da análise: fila, processo, documentos, busca, painel, avaliação e registro auditável. A faixa no topo de cada tela lista o que é simulado.

## Executar

Requer Nix com flakes. Na raiz do repositório:

```bash
nix run
```

Abra <http://127.0.0.1:8000>. A demonstração funciona sem rede e sem chave de API: ela restaura o estado da análise já concluída, com as respostas do modelo em cache. O texto dos documentos já vem incluído; o link para o PDF original só funciona depois de baixar o corpus, como descrito em [Reproduzir a avaliação](#reproduzir-a-avaliação).

## Resultado

Medido em 500 processos sintéticos, na primeira execução após congelar a lógica de decisão.

| # | Medida | Parâmetro do edital | Medido |
|---|---|---|---|
| 1 | Processos por ciclo | ≥ 500 | 500 |
| 2 | Taxa de acerto por processo | ≥ 80% | 94,0% |
| 3 | Tempo de máquina por processo | Bem abaixo de 163,5 min | 0,19 min |
| 4 | Análises com registro auditável | 100% | 100% |
| 5 | Integração com SEI e SINCIN+ | Comprovada até M1 | Não demonstrada: ambos simulados |

Estes números não representam desempenho em processos reais. Prestação de contas ficou abaixo da barra, com 72,0%, e sem o modelo de linguagem as regras caem para 46,8% em texto inédito. O tempo de máquina não mede redução do trabalho do analista.

O [relatório de avaliação](docs/relatorio-de-avaliacao.md) traz as falhas por critério, as causas e os limites.

## Documentos

- [Relatório de avaliação](docs/relatorio-de-avaliacao.md)
- [Rascunho do Anexo VI, Bloco 2](docs/proposta-anexo-vi-bloco-2.md)
- [Decisões e motivos](docs/decisoes.md)
- [Vídeo de demonstração](demo/demonstracao.mp4)

## Desenvolvimento

`nix develop` abre o ambiente com Python, Tesseract, ffmpeg e Playwright. Testes ficam em `tests/`.

```bash
python -m pytest tests/test_checks.py
python -m unicont_poc.cli gerar desenvolvimento
python -m unicont_poc.cli avaliar desenvolvimento --modo regras
```

### Publicar o site

```bash
python -m unicont_poc.cli exportar-site --base /sefaz-pi-cpsi-unicont-poc
python -m pytest tests/test_site_in_browser.py
```

O comando restaura `dados/estado-demo.sqlite.gz` em um banco temporário, renderiza os mesmos templates da aplicação e grava em `var/site`, que não pode existir antes. A publicação em GitHub Pages está em `.github/workflows/publicar-site.yml`. O teste de navegador aceita `UNICONT_SITE_URL` para rodar contra o endereço publicado.

No site, a busca usa [SQLite em WebAssembly](https://www.npmjs.com/package/@sqlite.org/sqlite-wasm), versão copiada para `web/site_estatico/vendor`, com a mesma consulta FTS5 do servidor. Aprovar e devolver ficam no `localStorage` do navegador.

### Reproduzir a avaliação

O replay do modelo exige o corpus exato da avaliação, porque as chaves do cache dependem do texto lido por OCR. Gerar de novo a partir da semente reproduz o gabarito e os documentos de texto, mas não as imagens digitalizadas, cujo ruído não tem semente. Por isso o corpus está publicado como anexo da [versão `avaliacao-1`](https://github.com/Castrozan/sefaz-pi-cpsi-unicont-poc/releases/tag/avaliacao-1):

```bash
gh release download avaliacao-1 -R Castrozan/sefaz-pi-cpsi-unicont-poc -p 'corpus-avaliacao.tar.gz'
mkdir -p var/corpus && tar xzf corpus-avaliacao.tar.gz -C var/corpus
python -m unicont_poc.cli avaliar avaliacao --modo modelo
python -m unicont_poc.cli avaliar avaliacao --modo regras
```

### Trocar o modelo de linguagem

O pipeline depende apenas da interface `LanguageModel` em `src/unicont_poc/ports.py`. Para outro fornecedor ou modelo local, implemente `complete` e passe a instância para `LanguageModelReview`. `AnthropicMessagesModel` é o adaptador para a API da Anthropic, com `claude-sonnet-5-5` como padrão, e lê `ANTHROPIC_API_KEY`. Ele está coberto por teste com cliente simulado e ainda não fez nenhuma chamada real.

As respostas em cache vieram de lotes de subagentes do Claude Code, porque não havia chave de API disponível. O motivo está nas [decisões](docs/decisoes.md).

### Trocar SEI e SINCIN+

`SeiGateway` e `SincinPlusGateway`, também em `ports.py`, isolam os sistemas externos. Os adaptadores reais dependem da documentação das APIs, prevista para o Marco P1. O adaptador do SINCIN+ deve manter a recusa a análises sem aprovação do analista.

## Licença

Código público para consulta, sem licença de uso concedida.
