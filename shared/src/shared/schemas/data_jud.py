
from pydantic import BaseModel, ConfigDict, Field


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
    codigo: int
    nome: str
    data_hora: str = Field(..., alias="dataHora")
    orgao_julgador: OrgaoJulgador | None = Field(default=None, alias="orgaoJulgador")

class OrgaoJulgador1(BaseModel):
    codigo_municipio_ibge: int = Field(..., alias="codigoMunicipioIBGE")
    codigo: int
    nome: str


class Assunto(BaseModel):
    codigo: int
    nome: str


class Source(BaseModel):
    numero_processo: str = Field(..., alias="numeroProcesso")
    classe: Classe
    sistema: Sistema
    formato: Formato
    tribunal: str
    data_hora_ultima_atualizacao: str = Field(..., alias="dataHoraUltimaAtualizacao")
    grau: str
    timestamp: str = Field(..., alias='@timestamp')
    data_ajuizamento: str = Field(..., alias="dataAjuizamento")
    movimentos: list[Movimento]
    id: str
    nivel_sigilo: int = Field(..., alias="nivelSigilo")
    orgao_julgador: OrgaoJulgador1 = Field(..., alias="orgaoJulgador")
    assuntos: list[Assunto]


class SearchHit(BaseModel):
    source: Source = Field(alias="_source")


class SearchHits(BaseModel):
    hits: list[SearchHit]


class SearchResponse(BaseModel):
    hits: SearchHits


# ------------------ RESUMIDO ------------------

class MovimentoResumido(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    nome: str
    data_hora: str = Field(..., alias="dataHora")
    orgao_julgador: str | None = Field(default=None, alias="orgaoJulgador")


class ProcessoResumido(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    numero_processo: str | None = Field(default=None, alias="numeroProcesso")
    classe: str | None = None
    sistema: str | None = None
    formato: str | None = None
    tribunal: str | None = None
    data_hora_ultima_atualizacao: str | None = Field(default=None, alias="dataHoraUltimaAtualizacao")
    grau: str | None = None
    timestamp: str = Field(..., alias='@timestamp')
    data_ajuizamento: str | None = Field(default=None, alias="dataAjuizamento")
    id: str | None = None
    orgao_julgador: str | None = Field(default=None, alias="orgaoJulgador")
    assuntos: list[str] | None = None
    movimentos: list[MovimentoResumido] | None = None


class ProcessoResumidoResponse(BaseModel):
    processos: list[ProcessoResumido]

