
from typing import Literal

from pydantic import BaseModel, Field


class Classe(BaseModel):
    codigo: int
    nome: str


class OrgaoJulgador(BaseModel):
    codigo_municipio_ibge: int | None = Field(default=None, alias="codigoMunicipioIBGE", description="Código do município no IBGE, se aplicável")
    codigo: int
    nome: str


class Movimento(BaseModel):
    codigo: int
    nome: str
    data_hora: str = Field(..., alias="dataHora")
    orgao_julgador: OrgaoJulgador | None = Field(default=None, alias="orgaoJulgador")


class Assunto(BaseModel):
    codigo: int
    nome: str


class Processo(BaseModel):
    assuntos: list[Assunto]
    classe: Classe
    data_ajuizamento: str = Field(..., alias="dataAjuizamento")
    data_hora_ultima_atualizacao: str = Field(..., alias="dataHoraUltimaAtualizacao")
    grau: str
    id: str
    # movimentos: list[Movimento]
    numero_processo: str = Field(..., alias="numeroProcesso")
    orgao_julgador: OrgaoJulgador = Field(..., alias="orgaoJulgador")
    timestamp: str = Field(..., alias='@timestamp')
    tribunal: str


class SearchHit(BaseModel):
    source: Processo = Field(alias="_source")


class SearchHits(BaseModel):
    hits: list[SearchHit]


class SearchResponse(BaseModel):
    hits: SearchHits


class ProcessoResumo(BaseModel):
    numero_processo: str
    grau: str
