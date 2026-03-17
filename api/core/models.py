from django.db import models


class DataJudSource(models.Model):
    numero_processo = models.CharField(max_length=64)
    tribunal = models.CharField(max_length=32)
    grau = models.CharField(max_length=32)
    data_ajuizamento = models.CharField(max_length=64, blank=True)
    data_ultima_atualizacao = models.CharField(max_length=64, blank=True)
    source_id = models.CharField(max_length=128, blank=True)
    assuntos = models.JSONField(default=list)
    movimentos = models.JSONField(default=list)
    raw_source = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "datajud_sources"
        constraints = [
            models.UniqueConstraint(
                fields=["numero_processo", "tribunal", "grau"],
                name="uniq_datajud_numero_tribunal_grau",
            )
        ]
