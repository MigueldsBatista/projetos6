import logging

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger("ingestion")
from __future__ import annotations
import logging
import sys
import requests
from pje_scraper.worker import run_pipeline
from shared.schemas.data_jud import (
    MovimentoResumido,
    ProcessoResumido,
    ProcessoResumidoResponse,
    SearchResponse,
)

trigger = "--trigger" in sys.argv
if trigger:
    print("Running pipeline on TRIGGER MODE\n")

topicos = [
    "Aposentadoria e Pensão",
    # "Categoria Profissional Especial",
    # "Contrato Individual de Trabalho",
    # "Direito Coletivo do Trabalho",
    # "Direito de Greve / Lockout",
    # "Direito Individual do Trabalho",
    # "Direito Sindical e Questões Análogas",
    # "Duração do Trabalho",
    # "Férias",
    # "Outras Relações de Trabalho",
    # "Prescrição",
    # "Prescrição e Decadência no Direito do Trabalho",
    # "Questões de Alta Complexidade, Grande Impacto e Repercussão",
    # "Redução à Condição Análoga à de Escravo",
    # "Rescisão do Contrato de Trabalho",
    # "Rescisão do Contrato de Trabalho",
    # "Responsabilidade Civil do Empregador",
    # "Responsabilidade Solidária / Subsidiária",
    # "Sentença Normativa",
    # "Verbas Remuneratórias, Indenizatórias e Benefícios",
]

url = "https://api-publica.datajud.cnj.jus.br/api_publica_trt6/_search"

public_key = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="

headers = {"Authorization": f"APIKey {public_key}"}


def mapear_processos(search_response: SearchResponse) -> ProcessoResumidoResponse:
    processos = []
    for hit in search_response.hits.hits:
        processos.append(
            ProcessoResumido(
                numero_processo=hit.source.numero_processo,
                classe=hit.source.classe.nome,
                sistema=hit.source.sistema.nome,
                formato=hit.source.formato.nome,
                tribunal=hit.source.tribunal,
                data_hora_ultima_atualizacao=hit.source.data_hora_ultima_atualizacao,
                grau="2" if hit.source.grau == "G2" else "1",
                timestamp=hit.source.timestamp,
                data_ajuizamento=hit.source.data_ajuizamento,
                movimentos=[
                    MovimentoResumido(
                        nome=m.nome,
                        data_hora=m.data_hora,
                        orgao_julgador=m.orgao_julgador.nome if m.orgao_julgador else None,
                    )
                    for m in hit.source.movimentos
                ],
                id=hit.source.id,
                orgao_julgador=hit.source.orgao_julgador.nome,
                assuntos=[a.nome for a in hit.source.assuntos],
            )
        )

    return ProcessoResumidoResponse(processos=processos)


def fetch_for_topic(topic):
    query = {"size": 100, "query": {"bool": {"must": [{"match": {"assuntos.nome": topic}}]}}}
    response = requests.get(url, headers=headers, json=query, timeout=30)
    response.raise_for_status()
    return response.json()


def main():
    """
    Pipeline principal de ingestão:
    1. Consulta tópicos no DataJud.
    2. Salva/processos encontrados em JSON.
    3. Envia/processos completos para API de deduplicação.
    4. (Opcional) Dispara workers para extração PDF.

    Pontos de extensão:
    - Adicionar etapa de verificação de existência em nuvem/bucket.
    - Modularizar etapas para facilitar manutenção.
    - Adicionar métricas e monitoramento.
    """
    # TODO: Adicionar etapa de verificação dos processos que ainda não existem no bucket/cloud
    # Exemplo: verificar existência de arquivos PDF antes de disparar workers

    import json


    total_processos = 0
    assuntos_sem_resultado = []
    todos_processos = []
    logger.info(f"Consultando {len(topicos)} assuntos do CNJ...")


    try:
        response = fetch_for_topic(assunto)
        search_response = SearchResponse.model_validate(response)
    except Exception as e:
        logger.error(f"Erro ao consultar '{assunto}': {e}")
        continue

    processos = mapear_processos(search_response)
    n = len(processos.processos)

    logger.info(f"  -> {n} processos encontrados para '{assunto}'")
    total_processos += n

    if n == 0:
        assuntos_sem_resultado.append(assunto)

    for p in processos.processos:
        todos_processos.append(p.model_dump())

    logger.info(f"Total de processos encontrados: {total_processos}")

    if assuntos_sem_resultado:
        logger.warning("Assuntos sem resultados:")
        for assunto in assuntos_sem_resultado:
            logger.warning(f"  - {assunto}")

    with open("processos_datajud.json", "w", encoding="utf-8") as f:
        json.dump(todos_processos, f, ensure_ascii=False, indent=2)

    logger.info(f"Arquivo processos_datajud.json salvo com {len(todos_processos)} processos.")

    # Enviar para API como JSON
    import requests
    try:
        res = requests.post(
            "http://localhost:8000/api/processos/deduplicar",
            timeout=30,
            json=todos_processos
        )
        res.raise_for_status()
        logger.info(f"Resposta da API ({res.status_code}): {res.json()}")
    except Exception as e:
        logger.error(f"Erro ao enviar para API: {e}")

    if trigger:
        for p in todos_processos:
            logger.info(f"Disparando worker para processo {p['numero_processo']} grau {p['grau']}")
            run_pipeline.delay(p["numero_processo"], p["grau"])


if __name__ == "__main__":
    main()
