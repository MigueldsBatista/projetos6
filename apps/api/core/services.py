from collections.abc import Mapping, Sequence
from datetime import date

from core.models.processo import Processo
from core.serializers import ProcessoDeduplicarDTO

N_PROCESSO = Processo.numero_processo.field.name
DT_ATUALIZACAO = Processo.data_hora_ultima_atualizacao.field.name

def filtrar_processos_faltantes(
    dados_entrada: Sequence[ProcessoDeduplicarDTO]
) -> list[ProcessoDeduplicarDTO]:

    numeros_entrada: list[str] = [p.numero_processo for p in dados_entrada]

    processos_no_banco = (
        Processo.objects
        .filter(**{f"{N_PROCESSO}__in": numeros_entrada})
        .values(N_PROCESSO, DT_ATUALIZACAO)
    )

    mapa_banco: Mapping[str, date | None] = {
        p[N_PROCESSO]: p[DT_ATUALIZACAO]
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
