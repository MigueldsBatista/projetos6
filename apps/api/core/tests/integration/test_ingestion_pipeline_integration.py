# ruff: noqa: S101, I001

import json
from pathlib import Path

import pytest
from core.models.processo import Processo
from ingestion.main import mapear_processos
from ingestion.providers import FileDataProvider
from ingestion.submitter import ProcessSubmitter

DEDUPLICAR_ENDPOINT = "/api/processos/deduplicar/"
DATAJUD_PATH = Path(__file__).resolve().parents[3] / "data" / "dataJud.json"


def _write_single_hit_fixture(tmp_path: Path) -> Path:
    with DATAJUD_PATH.open(encoding="utf-8") as source_file:
        raw = json.load(source_file)

    single_hit = {
        "hits": {
            "hits": [raw["hits"]["hits"][0]],
        }
    }

    fixture_path = tmp_path / "datajud_single_hit.json"
    fixture_path.write_text(json.dumps(single_hit, ensure_ascii=False), encoding="utf-8")
    return fixture_path


@pytest.mark.django_db(transaction=True)
def test_given_datajud_fixture_when_submit_to_deduplicar_then_persist_and_deduplicate(live_server, tmp_path):
    fixture_path = _write_single_hit_fixture(tmp_path)
    provider = FileDataProvider(str(fixture_path))

    search_response = provider.get_data(topic="Direito de Greve / Lockout")
    assert search_response is not None

    processos = mapear_processos(search_response)
    assert len(processos) == 1

    submitter = ProcessSubmitter(api_url=f"{live_server.url}{DEDUPLICAR_ENDPOINT}")

    first_response = submitter.submit(processos)
    assert first_response is not None
    assert len(first_response) == 1

    numero_processo = processos[0]["numero_processo"]
    assert Processo.objects.filter(numero_processo=numero_processo).count() == 1

    second_response = submitter.submit(processos)
    assert second_response == []
    assert Processo.objects.filter(numero_processo=numero_processo).count() == 1

