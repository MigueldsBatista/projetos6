# Endpoints necessarios ate agr

# Deduplicate Processes
# Recebe vários processos e retorna os processos ainda não presentes no banco, baseado no numero do processo e na última data de atualização

# Endpoint: POST /processos/deduplicar

# Adicionar Analise
# Recebe o numero do proesso e os campos provenientes da analise e adiciona ao processo correspondente

# Endpoint: POST /processos/adicionar-analise
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from core.serializers.processo_serializer import ProcessoResumoSerializer, ProcessoSerializer


class ProcessoViewset(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def bulk_create(self, request: Request):
        input_serializer = ProcessoSerializer(data=request.data, many=True)
        input_serializer.is_valid(raise_exception=True)

        created_items = input_serializer.save()

        output_serializer = ProcessoResumoSerializer(created_items, many=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
