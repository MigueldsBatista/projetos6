from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Classe(BaseModel):
    codigo: int
    nome: str


class Sistema(BaseModel):
    codigo: int
    nome: str


class Formato(BaseModel):
    codigo: int
    nome: str


class ComplementosTabelado(BaseModel):
    codigo: int
    valor: int | None = None
    nome: str
    descricao: str | None = None


class OrgaoJulgador(BaseModel):
    codigo: str
    nome: str


class Movimento(BaseModel):
    complementosTabelados: list[ComplementosTabelado] = []
    codigo: int
    nome: str
    dataHora: str
    orgaoJulgador: OrgaoJulgador | None = None


class OrgaoJulgador1(BaseModel):
    codigoMunicipioIBGE: int
    codigo: int
    nome: str


class Assunto(BaseModel):
    codigo: int
    nome: str


class Source(BaseModel):
    numeroProcesso: str
    classe: Classe
    sistema: Sistema
    formato: Formato
    tribunal: str
    dataHoraUltimaAtualizacao: str
    grau: str
    timestamp: str = Field(..., alias='@timestamp')
    dataAjuizamento: str
    movimentos: list[Movimento]
    id: str
    nivelSigilo: int
    orgaoJulgador: OrgaoJulgador1
    assuntos: list[Assunto]


class SearchHit(BaseModel):
    source: Source = Field(alias="_source")


class SearchHits(BaseModel):
    hits: list[SearchHit]


class SearchResponse(BaseModel):
    hits: SearchHits


def parse_sources(payload: SearchResponse | dict[str, Any]) -> list[Source]:
    """Parse DataJud search payload and return only the list of sources."""
    response = payload if isinstance(payload, SearchResponse) else SearchResponse.model_validate(payload)
    return [hit.source for hit in response.hits.hits]


class MatchClause(BaseModel):
    match: dict[str, str]


class BoolQuery(BaseModel):
    must: list[MatchClause]


class QueryClause(BaseModel):
    bool: BoolQuery


class SearchRequestPayload(BaseModel):
    size: int = 10
    query: QueryClause


