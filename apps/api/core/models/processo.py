
from django.db import models

from core.models.analise import Analise
from core.models.assunto import Assunto
from core.models.movimento import Movimento
from core.models.orgao_julgador import OrgaoJulgador


class Processo(models.Model):
    numero_processo = models.CharField(max_length=20, blank=False)
    classe = models.CharField(max_length=128, blank=True)
    tribunal = models.CharField(max_length=32, blank=True)
    data_hora_ultima_atualizacao = models.DateField(blank=True, null=True)
    grau = models.CharField(max_length=32, blank=True) #G1 ou G2
    data_ajuizamento = models.DateField(blank=True, null=True)
    orgao_julgador = models.ForeignKey(OrgaoJulgador, on_delete=models.SET_NULL, blank=True, null=True)
    assuntos = models.ManyToManyField(Assunto, blank=True, default=list)
    movimentos = models.ManyToManyField(Movimento, blank=True, default=list)
    analise = models.OneToOneField(Analise, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = "datajud_sources" # Mudar
        constraints = [
            models.UniqueConstraint(
                fields=["numero_processo", "tribunal", "grau"],
                name="uniq_datajud_numero_tribunal_grau",
            )
        ]


    def __str__(self) -> str:
        return self.numero_processo
