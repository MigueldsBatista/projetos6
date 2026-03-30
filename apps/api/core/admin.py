# Register your models here.

from django.contrib import admin

from core.models.analise import Analise
from core.models.movimento import Movimento
from core.models.orgao_julgador import OrgaoJulgador
from core.models.palavra_chave import PalavraChave
from core.models.processo import Processo

admin.site.register(Analise)
admin.site.register(Movimento)
admin.site.register(OrgaoJulgador)
admin.site.register(PalavraChave)
admin.site.register(Processo)
