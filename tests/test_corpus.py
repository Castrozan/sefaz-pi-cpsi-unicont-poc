import hashlib
import json
from pathlib import Path

from unicont_poc.corpus.catalog import checklist_for
from unicont_poc.corpus.generation import CorpusRequest, generate_corpus
from unicont_poc.corpus.processes.identities import cnpj_check_digits
from unicont_poc.domain import ProcessCategory


def small_request(name: str) -> CorpusRequest:
    counts = {ProcessCategory.PAGAMENTO: 8, ProcessCategory.CONTRATACAO: 3, ProcessCategory.PRESTACAO_DE_CONTAS: 3}
    return CorpusRequest(name, 99, counts, ("padrao",))


def digest(directory: Path) -> str:
    return hashlib.sha256((directory / "manifesto.jsonl").read_bytes()).hexdigest()


def test_corpus_is_reproducible_from_the_seed(tmp_path):
    first = generate_corpus(small_request("a"), tmp_path, workers=2)
    second = generate_corpus(small_request("a"), tmp_path / "outra", workers=2)
    assert digest(first) == digest(second)


def test_gold_codes_exist_in_the_checklist_of_the_category(tmp_path):
    directory = generate_corpus(small_request("b"), tmp_path, workers=2)
    for line in (directory / "gabarito.jsonl").read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        known = {item.code for item in checklist_for(ProcessCategory(record["category"]))}
        assert set(record["irregularities"]) <= known


def test_manifest_does_not_leak_the_answer(tmp_path):
    directory = generate_corpus(small_request("c"), tmp_path, workers=2)
    manifest = (directory / "manifesto.jsonl").read_text(encoding="utf-8")
    assert "irregularities" not in manifest and "PAG-0" not in manifest


def test_cnpj_check_digits_match_a_known_valid_number():
    assert cnpj_check_digits("112223330001") == "81"
