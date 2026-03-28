from __future__ import annotations

import json

import requests
from pje_scraper.worker import run_pipeline
from shared.schemas import ProcessoResumido, ProcessoResumidoResponse, SearchResponse

topicos = [
    'Aposentadoria e Pensão',
		'Categoria Profissional Especial',
		'Contrato Individual de Trabalho',
		'Direito Coletivo do Trabalho',
		'Direito de Greve / Lockout',
		'Direito Individual do Trabalho',
		'Direito Sindical e Questões Análogas',
		'Duração do Trabalho',
		'Férias',
		'Outras Relações de Trabalho',
		'Prescrição',
		'Prescrição e Decadência no Direito do Trabalho',
		'Questões de Alta Complexidade, Grande Impacto e Repercussão',
		'Redução à Condição Análoga à de Escravo',
		'Rescisão do Contrato de Trabalho',
		'Rescisão do Contrato de Trabalho',
		'Responsabilidade Civil do Empregador',
		'Responsabilidade Solidária / Subsidiária',
		'Sentença Normativa',
		'Verbas Remuneratórias, Indenizatórias e Benefícios'
]

query_ = {
  "size": 100,
  "query": {
    "bool": {
      "must": [
        { "match": { "assuntos.nome": nome} } for nome in topicos
      ]
    }
  }
}


query = {
  "size": 10,
  "query": {
    "bool": {
      "must": [
        { "match": { "assuntos.nome": "Transporte Aéreo" } },
        { "match": { "assuntos.nome": "Indenização por Dano Moral" } }
      ]
    }
  }
}

url = "https://api-publica.datajud.cnj.jus.br/api_publica_trt6/_search"

headers = {
    "Authorization": "APIKey cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
}


def mapear_processos(search_response: SearchResponse) -> ProcessoResumidoResponse:
    processos = []
    for hit in search_response.hits.hits:
        processos.append(
            ProcessoResumido(
                numeroProcesso=hit.source.numeroProcesso,
                classe=hit.source.classe.nome,
                sistema=hit.source.sistema.nome,
                formato=hit.source.formato.nome,
                tribunal=hit.source.tribunal,
                dataHoraUltimaAtualizacao=hit.source.dataHoraUltimaAtualizacao,
                grau="2" if hit.source.grau == "G2" else "1",
                timestamp=hit.source.timestamp,
                dataAjuizamento=hit.source.dataAjuizamento,
                id=hit.source.id,
                orgaoJulgador=hit.source.orgaoJulgador.nome,
                assuntos=list(map(lambda a: a.nome, hit.source.assuntos))
            )
        )

    return ProcessoResumidoResponse(processos=processos)

def fetch():
    response = requests.get(url, headers=headers, json=query, timeout=30)
    response.raise_for_status()
    return response.json()

def main():
  response = fetch()
  print(len(response))
  search_response = SearchResponse.model_validate(response)
  processos = mapear_processos(search_response)
  for processo in processos.processos:
    run_pipeline.delay(processo.numeroProcesso, processo.grau)

if __name__ == "__main__":
  main()
