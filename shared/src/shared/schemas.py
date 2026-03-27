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


# ------------------ RESUMIDO ------------------

class ProcessoResumido(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    numeroProcesso: str | None = None
    classe: str | None = None
    sistema: str | None = None
    formato: str | None = None
    tribunal: str | None = None
    dataHoraUltimaAtualizacao: str | None = None
    grau: str | None = None
    timestamp: str = Field(..., alias='@timestamp')
    dataAjuizamento: str | None = None
    id: str | None = None
    orgaoJulgador: str | None = None
    assuntos: list[str] | None = None
    
    # nivelSigilo: int | None = None
    # movimentos: list[Movimento] | None = None


class ProcessoResumidoResponse(BaseModel):
    processos: list[ProcessoResumido]