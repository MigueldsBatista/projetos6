from copy import deepcopy
from datetime import date

from core.models.processo import Processo
from core.tests.constants import (
    DATA_BASE,
    GRAU_G1,
    PROCESSO_NUMERO_1,
    TRIBUNAL_TRT6,
)


class ProcessoPayloadBuilder:
    def __init__(self):
        self._payload = {
            "numero_processo": PROCESSO_NUMERO_1,
            "tribunal": TRIBUNAL_TRT6,
            "grau": GRAU_G1,
            "data_hora_ultima_atualizacao": DATA_BASE,
        }

    def with_numero_processo(self, numero_processo: str):
        self._payload["numero_processo"] = numero_processo
        return self

    def with_data_atualizacao(self, data_atualizacao: date | None):
        self._payload["data_hora_ultima_atualizacao"] = data_atualizacao
        return self

    def with_classe(self, codigo: str = "C001", nome: str = "Classe Teste"):
        self._payload["classe"] = {"codigo": codigo, "nome": nome}
        return self

    def with_orgao_julgador(
        self,
        codigo: int = 1001,
        nome: str = "Orgao Julgador Teste",
        codigo_municipio_ibge: int | None = None,
    ):
        self._payload["orgao_julgador"] = {
            "codigo": codigo,
            "nome": nome,
            "codigo_municipio_ibge": codigo_municipio_ibge,
        }
        return self

    def with_assuntos(self, assuntos: list[dict] | None = None):
        self._payload["assuntos"] = assuntos or [{"codigo": 2001, "nome": "Assunto Teste"}]
        return self

    def build(self) -> dict:
        return deepcopy(self._payload)


class DataSetup:
    @staticmethod
    def create_processo_existente(
        numero_processo: str,
        data_hora_ultima_atualizacao: date | None,
        tribunal: str = TRIBUNAL_TRT6,
        grau: str = GRAU_G1,
    ) -> Processo:
        return Processo.objects.create(
            numero_processo=numero_processo,
            tribunal=tribunal,
            grau=grau,
            data_hora_ultima_atualizacao=data_hora_ultima_atualizacao,
        )
