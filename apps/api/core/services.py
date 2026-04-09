
from collections.abc import Mapping, Sequence
from datetime import date

from core.models.processo import Processo


def filtrar_processos_faltantes(
    dados_entrada: Sequence[dict],
) -> list[dict]:
    numeros_entrada: list[str] = [item["numero_processo"] for item in dados_entrada]

    if not numeros_entrada:
        return []

    processos_no_banco = (
        Processo.objects
        .filter(numero_processo__in=numeros_entrada)
        .values("numero_processo", "data_hora_ultima_atualizacao")
    )

    mapa_banco: Mapping[str, date | None] = {
        item["numero_processo"]: item["data_hora_ultima_atualizacao"]
        for item in processos_no_banco
    }

    def precisa_de_processamento(item: dict) -> bool:
        data_banco: date | None = mapa_banco.get(item["numero_processo"])

        if item["numero_processo"] not in mapa_banco:
            return True

        if item.get("data_hora_ultima_atualizacao"):
            return data_banco is None or item["data_hora_ultima_atualizacao"] > data_banco

        return False

    return [item for item in dados_entrada if precisa_de_processamento(item)]
