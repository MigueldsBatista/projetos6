
from __future__ import annotations

from dateutil.parser import parse as parse_date
from pje_scraper.worker import run_pipeline
from shared.logger import get_logger
from shared.schemas.data_jud import SearchResponse

from ingestion.cli import IngestionParser
from ingestion.providers import DataProvider
from ingestion.submitter import ProcessSubmitter

logger = get_logger("ingestion_pipeline")

def get_topics():
    return [
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


def mapear_processos(search_response: SearchResponse) -> list[dict]:
   result = []
   for model in search_response.hits.hits:
        dump = model.source.model_dump()

        try:
            dump["data_ajuizamento"] = (
                parse_date(model.source.data_ajuizamento)
                .date()
                .isoformat()
            )
        except Exception:
            dump["data_ajuizamento"] = model.source.data_ajuizamento
        try:
            dump["data_hora_ultima_atualizacao"] = (
                parse_date(model.source.data_hora_ultima_atualizacao)
                .date()
                .isoformat()
            )
        except Exception:
            dump["data_hora_ultima_atualizacao"] = model.source.data_hora_ultima_atualizacao
        try:
            dump["@timestamp"] = parse_date(model.source.timestamp).isoformat()
        except Exception:
            dump["@timestamp"] = model.source.timestamp
        result.append(dump)

   return result

def fetch_for_topic(provider: DataProvider, topic: str) -> list[dict]:
    search_response = provider.get_data_and_persist(topic)

    if not search_response:
        logger.warning(f"Sem resultados ou erro para '{topic}'")
        return None

    logger.info(f"Resposta para '{topic}': {len(search_response.hits.hits)} processos encontrados")

    return mapear_processos(search_response)




def main():
    args = IngestionParser()
    provider = args.get_cli_provider()
    topics = get_topics()


    todos_processos = []
    submitter = ProcessSubmitter()
    logger.info(f"Consultando {len(topics)} assuntos do CNJ...")

    for assunto in topics:
        processos = fetch_for_topic(provider, assunto)

        if not processos:
            continue

        todos_processos.extend(processos)
        n = len(processos) if processos else 0
        logger.info(f"  -> {n} processos encontrados para '{assunto}'")

        api_response = submitter.submit(processos)
        if api_response is None:
            logger.error(f"Erro ao enviar processos para API para '{assunto}'")
            return

        logger.info(f"Processos para '{assunto}' enviados com sucesso. Resposta: {len(api_response)} retornados")

    if args.trigger:
        for p in todos_processos:
            logger.info(f"Disparando worker para processo {p['numero_processo']} grau {p['grau']}")
            run_pipeline.delay(p["numero_processo"], p["grau"])

if __name__ == "__main__":
    main()
