from django.db import models


class Document(models.Model):
    key = models.IntegerField(primary_key=True, db_column="KEY")
    num_acordao = models.FloatField(null=True, blank=True, db_column="NUMACORDAO")
    ano_acordao = models.FloatField(null=True, blank=True, db_column="ANOACORDAO")
    colegiado = models.TextField(null=True, blank=True, db_column="COLEGIADO")
    area = models.TextField(null=True, blank=True, db_column="AREA")
    tema = models.TextField(null=True, blank=True, db_column="TEMA")
    subtema = models.TextField(null=True, blank=True, db_column="SUBTEMA")
    enunciado = models.TextField(null=True, blank=True, db_column="ENUNCIADO")
    excerto = models.TextField(null=True, blank=True, db_column="EXCERTO")
    num_sumula = models.FloatField(null=True, blank=True, db_column="NUMSUMULA")
    data_sessao = models.TextField(null=True, blank=True, db_column="DATASESSAOFORMATADA")
    autor_tese = models.TextField(null=True, blank=True, db_column="AUTORTESE")
    funcao_autor_tese = models.TextField(null=True, blank=True, db_column="FUNCAOAUTORTESE")
    tipo_processo = models.TextField(null=True, blank=True, db_column="TIPOPROCESSO")
    tipo_recurso = models.TextField(null=True, blank=True, db_column="TIPORECURSO")
    indexacao = models.TextField(null=True, blank=True, db_column="INDEXACAO")
    indexadores_consolidados = models.TextField(null=True, blank=True, db_column="INDEXADORESCONSOLIDADOS")
    paragrafo_lc = models.TextField(null=True, blank=True, db_column="PARAGRAFOLC")
    referencia_legal = models.TextField(null=True, blank=True, db_column="REFERENCIALEGAL")
    publicacao_apresentacao = models.TextField(null=True, blank=True, db_column="PUBLICACAOAPRESENTACAO")
    paradigmatico = models.TextField(null=True, blank=True, db_column="PARADIGMATICO")

    class Meta:
        managed = False  # Django won't touch the existing table
        db_table = "docs"
