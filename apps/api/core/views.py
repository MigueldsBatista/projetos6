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

from core.serializers import ProcessoInputSerializer, to_dto
from core.services import filtrar_processos_faltantes


class ProcessoViewset(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def deduplicar(self, request: Request):
            input_serializer = ProcessoInputSerializer(data=request.data, many=True)
            input_serializer.is_valid(raise_exception=True)

            dtos_entrada = to_dto(input_serializer.validated_data)

            # Filtrar os processos faltantes
            dtos_faltantes = filtrar_processos_faltantes(dtos_entrada)

            # Criar os processos faltantes

            # Retornar os processos que conseguiram ser criados para que passem para proxima etama
            output_serializer = ProcessoInputSerializer(dtos_faltantes, many=True)

            return Response(output_serializer.data, status=status.HTTP_200_OK)
