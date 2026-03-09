from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Model(BaseModel):
    took: int
    timed_out: bool
    _shards: _Shards
    hits: Hits


class Hits(BaseModel):
    total: Total
    max_score: float
    hits: List[Hit]


class Hit(BaseModel):
    _index: str
    _id: str
    _score: float
    _source: _Source

class _Source(BaseModel):
    numeroProcesso: str
    classe: Classe
    sistema: Sistema
    formato: Formato
    tribunal: str
    dataHoraUltimaAtualizacao: str
    grau: str
    _timestamp: str = Field(..., alias='@timestamp')
    dataAjuizamento: str
    movimentos: List[Movimento]
    id: str
    nivelSigilo: int
    orgaoJulgador: OrgaoJulgador1
    assuntos: List[Assunto]


class _Shards(BaseModel):
    total: int
    successful: int
    skipped: int
    failed: int


class Total(BaseModel):
    value: int
    relation: str


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
    valor: int
    nome: str
    descricao: str


class OrgaoJulgador(BaseModel):
    codigo: str
    nome: str


class Movimento(BaseModel):
    complementosTabelados: Optional[List[ComplementosTabelado]] = None
    codigo: int
    nome: str
    dataHora: str
    orgaoJulgador: Optional[OrgaoJulgador] = None


class OrgaoJulgador1(BaseModel):
    codigoMunicipioIBGE: int
    codigo: int
    nome: str


class Assunto(BaseModel):
    codigo: int
    nome: str



