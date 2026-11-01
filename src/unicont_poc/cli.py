from __future__ import annotations

import argparse
import json
from pathlib import Path

from unicont_poc.adapters.language_models import PromptCollector, ReplayLanguageModel, request_key
from unicont_poc.analysis.cycle import read_cycle, run_cycle
from unicont_poc.analysis.pipeline import prepare_process
from unicont_poc.analysis.review.language_review import LanguageModelReview
from unicont_poc.analysis.review.rule_only_review import RuleOnlyReview
from unicont_poc.corpus.generation import CorpusRequest, generate_corpus
from unicont_poc.domain import ProcessCategory
from unicont_poc.evaluation.runner import evaluate
from unicont_poc.persistence.store import AnalysisStore

CORPUS_ROOT = Path("var/corpus")
STATE_ROOT = Path("var/estado")
CORPUS_PRESETS = {
    "desenvolvimento": CorpusRequest(
        "desenvolvimento",
        20261031,
        {ProcessCategory.PAGAMENTO: 60, ProcessCategory.CONTRATACAO: 20, ProcessCategory.PRESTACAO_DE_CONTAS: 20},
        ("padrao",),
    ),
    "avaliacao": CorpusRequest(
        "avaliacao",
        20261101,
        {ProcessCategory.PAGAMENTO: 300, ProcessCategory.CONTRATACAO: 100, ProcessCategory.PRESTACAO_DE_CONTAS: 100},
        ("padrao", "inedita"),
    ),
}


def _review_stage(mode: str, replies: Path):
    if mode == "regras":
        return RuleOnlyReview()
    return LanguageModelReview(ReplayLanguageModel(replies))


def command_generate(arguments: argparse.Namespace) -> None:
    print(generate_corpus(CORPUS_PRESETS[arguments.preset], CORPUS_ROOT))


def command_evaluate(arguments: argparse.Namespace) -> None:
    corpus_directory = CORPUS_ROOT / arguments.preset
    database = STATE_ROOT / f"{arguments.preset}-{arguments.mode}.sqlite"
    database.unlink(missing_ok=True)
    store = AnalysisStore(database)
    review = _review_stage(arguments.mode, Path(arguments.replies))
    cycle = run_cycle(corpus_directory, review, store, arguments.workers)
    report = evaluate(corpus_directory, cycle, store)
    output = Path(arguments.output or f"var/relatorios/{arguments.preset}-{arguments.mode}.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps({key: report[key] for key in ("global", "acerto_ponderado_pela_composicao_real", "tempo")}, indent=2)
    )


def command_export_prompts(arguments: argparse.Namespace) -> None:
    collector = PromptCollector()
    review = LanguageModelReview(collector)
    for view, _ in read_cycle(CORPUS_ROOT / arguments.preset, arguments.workers):
        prepare_process(view, review)
    output = Path(arguments.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as prompts:
        for key, request in collector.requests.items():
            prompts.write(json.dumps({"key": key, "prompt": request.user_prompt}, ensure_ascii=False) + "\n")
    print(
        f"{len(collector.requests)} pedidos em {output}; chave de exemplo {request_key(next(iter(collector.requests.values())))}"
    )


def command_import_replies(arguments: argparse.Namespace) -> None:
    requests = {}
    for line in Path(arguments.pedidos).read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        requests[record["key"]] = record
    cache_path = Path(arguments.replies)
    known = set()
    if cache_path.exists():
        known = {json.loads(line)["key"] for line in cache_path.read_text(encoding="utf-8").splitlines()}
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    imported = malformed = 0
    with cache_path.open("a", encoding="utf-8") as cache:
        for line in Path(arguments.lote).read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            if record["key"] not in requests or record["key"] in known:
                malformed += 1
                continue
            text = record["text"] if isinstance(record["text"], str) else json.dumps(record["text"], ensure_ascii=False)
            cache.write(
                json.dumps(
                    {
                        "key": record["key"],
                        "text": text,
                        "model_identifier": arguments.modelo,
                        "execution_mode": "lote-subagente-claude-code",
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            known.add(record["key"])
            imported += 1
    print(f"importados {imported}; ignorados {malformed}; total {len(known)}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="unicont-poc")
    commands = parser.add_subparsers(required=True)
    generate = commands.add_parser("gerar")
    generate.add_argument("preset", choices=CORPUS_PRESETS)
    generate.set_defaults(handler=command_generate)
    evaluation = commands.add_parser("avaliar")
    evaluation.add_argument("preset", choices=CORPUS_PRESETS)
    evaluation.add_argument("--modo", dest="mode", choices=("regras", "modelo"), default="regras")
    evaluation.add_argument("--respostas", dest="replies", default="dados/respostas-do-modelo.jsonl")
    evaluation.add_argument("--saida", dest="output")
    evaluation.add_argument("--processos", dest="workers", type=int, default=6)
    evaluation.set_defaults(handler=command_evaluate)
    export = commands.add_parser("exportar-pedidos")
    export.add_argument("preset", choices=CORPUS_PRESETS)
    export.add_argument("--saida", dest="output", required=True)
    export.add_argument("--processos", dest="workers", type=int, default=6)
    export.set_defaults(handler=command_export_prompts)
    importing = commands.add_parser("importar-respostas")
    importing.add_argument("--pedidos", required=True)
    importing.add_argument("--lote", required=True)
    importing.add_argument("--modelo", required=True)
    importing.add_argument("--respostas", dest="replies", default="dados/respostas-do-modelo.jsonl")
    importing.set_defaults(handler=command_import_replies)
    arguments = parser.parse_args()
    arguments.handler(arguments)


if __name__ == "__main__":
    main()
