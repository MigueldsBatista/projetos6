from __future__ import annotations

import requests
from pje_scraper.worker import run_pipeline
from shared.schemas.data_jud import (
    MovimentoResumido,
    ProcessoResumido,
    ProcessoResumidoResponse,
    SearchResponse,
)

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

    import json

    total_processos = 0
    assuntos_sem_resultado = []
    todos_processos = []
    print(f"Consultando {len(topicos)} assuntos do CNJ...")

    for assunto in topicos:
        print(f"Consultando assunto: {assunto}")

        response = fetch_for_topic(assunto)
        search_response = SearchResponse.model_validate(response)

        processos = mapear_processos(search_response)
        n = len(processos.processos)

        print(f"  -> {n} processos encontrados para '{assunto}'")
        total_processos += n

        if n == 0:
            assuntos_sem_resultado.append(assunto)

        for p in processos.processos:
            todos_processos.append(p.model_dump())

    print(f"Total de processos encontrados: {total_processos}")

    if assuntos_sem_resultado:
        print("Assuntos sem resultados:")
        for assunto in assuntos_sem_resultado:
            print(f"  - {assunto}")

    with open("processos_datajud.json", "w", encoding="utf-8") as f:
        json.dump(todos_processos, f, ensure_ascii=False, indent=2)

    print(f"Arquivo processos_datajud.json salvo com {len(todos_processos)} processos.")

    # for p in todos_processos:
    #     run_pipeline.delay(p["numeroProcesso"], p["grau"])


if __name__ == "__main__":
    main()
