from enum import StrEnum

from pydantic import BaseModel, Field


class EnumWithChoices(StrEnum):

    @classmethod
    def choices(cls):
        # Retorna uma lista de tuplas: [('sentenca', 'Sentenca'), ...]
        # .replace('_', ' ').title() transforma 'acordo_homologado' em 'Acordo Homologado'
        return [(key.value, key.name.replace('_', ' ').title()) for key in cls]

class TipoAtoPrincipal(EnumWithChoices):
    ACORDO_HOMOLOGADO = "acordo_homologado"
    SENTENCA = "sentenca"
    ACORDAO = "acordao"
    DESPACHO = "despacho"
    OUTRO = "outro"

class StatusProcesso(EnumWithChoices):
    ARQUIVADO = "arquivado"
    ACORDO_HOMOLOGADO = "acordo_homologado"
    SENTENCIADO = "sentenciado"
    EM_ANDAMENTO = "em_andamento"

class Desfecho(EnumWithChoices):
    ACORDO_FAVORAVEL = "acordo_favoravel"
    SENTENCA_PROCEDENTE = "sentenca_procedente"
    SENTENCA_PARCIALMENTE_PROCEDENTE = "sentenca_parcialmente_procedente"
    SENTENCA_IMPROCEDENTE = "sentenca_improcedente"
    EXTINTA = "extinta"
    ARQUIVADO_SEM_DECISAO = "arquivado_sem_decisao"
    OUTRO = "outro"

class ResultadoReclamante(EnumWithChoices):
    GANHOU = "ganhou"
    GANHOU_PARCIAL = "ganhou_parcial"
    PERDEU = "perdeu"
    SEM_DECISAO = "sem_decisao"


class ProcessoAnalise(BaseModel):
    numero_processo: str | None = Field(default=None, description="Número do processo")
    resumo: str | None = Field(default=None, description="Resumo do detalhado do motivo da ação")
    tipo_ato_principal: TipoAtoPrincipal | None = Field(default=None, description="Tipo do principal ato processual")
    decisao: str | None = Field(default=None, description="Resumo da decisão principal")
    palavras_chave: list[str | None] = Field(
        default=None, description="Lista de palavras-chave do processo", min_length=10
    )
    status: StatusProcesso | None = Field(default=None, description="Status atual do processo")
    desfecho: Desfecho | None = Field(default=None, description="Desfecho principal")
    resultado_reclamante: ResultadoReclamante | None = Field(default=None, description="Resultado para o reclamante")
    valor_causa: float | None = Field(default=None, description="Valor da causa")
    custas_valor_total: float | None = Field(default=None, description="Valor total das custas")
