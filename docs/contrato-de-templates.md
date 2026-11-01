# Contrato de templates do corpus sintético

Uma família de templates implementa `TemplateFamily` (`src/unicont_poc/corpus/contract.py`): recebe um `DocumentPlan` e
devolve `DocumentDraft(title, paragraphs)`. `title` pode ser `None` para documentos sem cabeçalho.

Os slots de cada `DocumentType` são os argumentos nomeados de `writer.add(...)` em `corpus/payment_process.py`,
`payment_commitments.py`, `payment_certificates.py`, `contracting_process.py`, `accountability_process.py` e
`blueprint.py` (`add_routine_paperwork`). Todo documento recebe também `process_number`, `organ_name`, `organ_cnpj` e
`sei_number`. Datas chegam como `date`, valores como `Decimal`.

Um leitor humano precisa conseguir recuperar de cada documento todos os fatos dos slots: a família muda a forma, nunca o
fato. Uma ressalva de execução continua sendo uma ressalva de execução, ainda que redigida de outro modo.

## Semântica dos slots categóricos

| # | Slot | Valor | Significado |
|---|---|---|---|
| 1 | `statement_kind` | `sem_ressalva` | recebimento integral |
| 2 | `statement_kind` | `ressalva_execucao` | `exception_detail` é uma falha real de execução, não sanada |
| 3 | `statement_kind` | `ressalva_afastada` | `exception_detail` é um incidente já resolvido, sem glosa |
| 4 | `opinion_kind` | `favoravel` | parecer favorável, sem condição |
| 5 | `opinion_kind` | `desfavoravel` | parecer contrário por `opinion_detail` |
| 6 | `opinion_kind` | `ressalva_pendente` | prosseguimento condicionado a corrigir `opinion_detail` |
| 7 | `opinion_kind` | `recomendacao_atendida` | favorável; `opinion_detail` já foi cumprido |
| 8 | `kind` (empenho) | `original` / `reforco` | empenho ordinário ou reforço |
| 9 | `fiscal_name` vazio no contrato | | contrato sem fiscal nominalmente indicado |
