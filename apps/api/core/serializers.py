

from rest_framework import serializers


class OrgaoJulgadorSerializer(serializers.Serializer):
    codigo = serializers.CharField()
    nome = serializers.CharField()

class MovimentoResumidoSerializer(serializers.Serializer):
    nome = serializers.CharField()
    data_hora = serializers.DateTimeField()
    orgao_julgador = OrgaoJulgadorSerializer(required=False, allow_null=True)

class ProcessoCompletoSerializer(serializers.Serializer):
    id = serializers.CharField()
    numero_processo = serializers.CharField()
    classe = serializers.CharField()
    sistema = serializers.CharField()
    formato = serializers.CharField()
    tribunal = serializers.CharField()
    data_hora_ultima_atualizacao = serializers.DateTimeField()
    grau = serializers.CharField()
    timestamp = serializers.DateTimeField()
    data_ajuizamento = serializers.DateField()
    movimentos = MovimentoResumidoSerializer(many=True)
    orgao_julgador = OrgaoJulgadorSerializer()
    assuntos = serializers.ListField(child=serializers.CharField())

class ProcessoInputSerializer(serializers.Serializer):
    numero_processo = serializers.CharField()
    data_hora_ultima_atualizacao = serializers.DateField(required=False, allow_null=True)

