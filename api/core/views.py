from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny

from .models import Document
from .serializers import DocumentSerializer


class DocumentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Read-only viewset: GET /api/documents/ and GET /api/documents/{id}/"""
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'key', 'num_acordao', 'ano_acordao', 'colegiado', 'area',
        'tema', 'subtema', 'tipo_processo', 'tipo_recurso',
        'autor_tese', 'paradigmatico',
    ]
