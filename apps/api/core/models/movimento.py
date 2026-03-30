from django.db import models

from core.models.orgao_julgador import OrgaoJulgador


class Movimento(models.Model):
    nome = models.CharField(max_length=128)
    data_hora = models.CharField(max_length=64)
    orgao_julgador = models.ForeignKey(OrgaoJulgador, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self) -> str:
        return self.nome
