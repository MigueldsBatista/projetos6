from __future__ import annotations

import pathlib
import sys

import requests
from dateutil.parser import parse as parse_date
from pje_scraper.worker import run_pipeline
from shared.logger import get_logger
from shared.schemas import safe_validate_model
from shared.schemas.data_jud import SearchResponse

logger = get_logger("ingestion_pipeline")

WORKSPACE = pathlib.Path(__file__).parent

trigger = "--trigger" in sys.argv
if trigger:
    print("Running pipeline on TRIGGER MODE\n")

topicos = [
    "Aposentadoria e Pensão",
    "Categoria Profissional Especial",
    "Contrato Individual de Trabalho",
    "Direito Coletivo do Trabalho",
    "Direito de Greve / Lockout",
    "Direito Individual do Trabalho",
    "Direito Sindical e Questões Análogas",
    "Duração do Trabalho",
    "Férias",
    "Outras Relações de Trabalho",
    "Prescrição",
    "Prescrição e Decadência no Direito do Trabalho",
    "Questões de Alta Complexidade, Grande Impacto e Repercussão",
    "Redução à Condição Análoga à de Escravo",
    "Rescisão do Contrato de Trabalho",
    "Rescisão do Contrato de Trabalho",
    "Responsabilidade Civil do Empregador",
    "Responsabilidade Solidária / Subsidiária",
    "Sentença Normativa",
    "Verbas Remuneratórias, Indenizatórias e Benefícios",
]

url = "https://api-publica.datajud.cnj.jus.br/api_publica_trt6/_search"

public_key = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="

headers = {"Authorization": f"APIKey {public_key}"}


def mapear_processos(search_response: SearchResponse) -> list[dict]:
   result = []
   for model in search_response.hits.hits:
        dump = model.source.model_dump()
        # Always send as YYYY-MM-DD
        try:
            dump["data_ajuizamento"] = parse_date(model.source.data_ajuizamento).date().isoformat()
        except Exception:
            dump["data_ajuizamento"] = model.source.data_ajuizamento
        try:
            dump["data_hora_ultima_atualizacao"] = parse_date(model.source.data_hora_ultima_atualizacao).date().isoformat()
        except Exception:
            dump["data_hora_ultima_atualizacao"] = model.source.data_hora_ultima_atualizacao
        try:
            dump["@timestamp"] = parse_date(model.source.timestamp).isoformat()
        except Exception:
            dump["@timestamp"] = model.source.timestamp
        result.append(dump)

   return result


def fetch_for_topic(topic, save=False, local=False) -> list[dict]:

    if local:
        with open(WORKSPACE / f"processos_{topic.replace(' ', '_')}.json", encoding="utf-8") as f:
            return f.read()

    query = {
        "size": 10,
        "query": {
            "bool": {
                "must": [
                    {"match": {"assuntos.nome": topic}}
                    ]
                }
            }
        }

    response = requests.get(
        url=url,
        headers=headers,
        json=query,
        timeout=30
    )

    if not response.ok:
        logger.warning(f"Sem resultados para '{topic}'")
        return None

    if save:
        with open(WORKSPACE / f"processos_{topic.replace(' ', '_')}.json", "w", encoding="utf-8") as f:
            f.write(response.text)
            logger.info(f"Resposta para '{topic}' salva em 'processos_{topic.replace(' ', '_')}.json'")

    search_response, validation_error = safe_validate_model(SearchResponse, response.json())

    if validation_error:
        logger.error(f"Erro ao validar resposta para '{topic}': {validation_error}")
        return None

    print(f"Resposta para '{topic}': {len(search_response.hits.hits)} processos encontrados")
    return mapear_processos(search_response)


def main():
    # TODO: Adicionar etapa de verificação dos processos que ainda não existem no bucket/cloud
    # Exemplo: verificar existência de arquivos PDF antes de disparar workers

    todos_processos = []

    logger.info(f"Consultando {len(topicos)} assuntos do CNJ...")

    for assunto in topicos:
        processos = fetch_for_topic(assunto, save=True)

        if not processos:
            continue

        todos_processos.extend(processos)

        n = len(processos) if processos else 0
        logger.info(f"  -> {n} processos encontrados para '{assunto}'")

        logger.info("Enviando processos para API de deduplicação...")

        res = requests.post("http://localhost:8000/api/processos/bulk_create/", timeout=30, json=processos)

        if not res.ok:
            logger.error(f"Erro ao enviar processos para API: {res.status_code} - {res.text}")
            return

        logger.info(f"Processos para '{assunto}' enviados com sucesso. Resposta: {res.status_code}")

        # TODO - adicionar logica para usar resposta da API para disparar os processos
        # TODO - Adicionar lógica para verificar processos na cloud e disparar os que que não existem, além dos presentes na resposta



    if trigger:
        for p in todos_processos:
            logger.info(f"Disparando worker para processo {p['numero_processo']} grau {p['grau']}")
            run_pipeline.delay(p["numero_processo"], p["grau"])


if __name__ == "__main__":
    main()
