from collections.abc import Mapping, Sequence
from datetime import date

from core.models.processo import Processo
from core.serializers import ProcessoDeduplicarDTO

FIELD_NUMERO = Processo.numero_processo.field.name
FIELD_DATA_UP = Processo.data_hora_ultima_atualizacao.field.name

def filtrar_processos_faltantes(
    dados_entrada: Sequence[ProcessoDeduplicarDTO]
) -> list[ProcessoDeduplicarDTO]:
    """
    Identifica processos que não existem no banco ou que possuem data de
    atualização posterior à registrada.
    """

    numeros_entrada: list[str] = [p.numero_processo for p in dados_entrada]

    processos_no_banco = (
        Processo.objects
        .filter(**{f"{FIELD_NUMERO}__in": numeros_entrada})
        .values(FIELD_NUMERO, FIELD_DATA_UP)
    )

    mapa_banco: Mapping[str, date | None] = {
        p[FIELD_NUMERO]: p[FIELD_DATA_UP]
        for p in processos_no_banco
    }

    def precisa_de_processamento(item: ProcessoDeduplicarDTO) -> bool:
        data_banco: date | None = mapa_banco.get(item.numero_processo)

        if item.numero_processo not in mapa_banco:
            return True

        if item.data_hora_ultima_atualizacao:
            return data_banco is None or item.data_hora_ultima_atualizacao > data_banco

        return False

    return [item for item in dados_entrada if precisa_de_processamento(item)]
