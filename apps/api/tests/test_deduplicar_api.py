import pytest
from core.models.processo import Processo
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_deduplicar_cria_novos_processos():
    client = APIClient()
    url = reverse('processoviewset-deduplicar')
    data = [
        {
            "numero_processo": "0001",
            "classe": "A",
            "tribunal": "TRT6",
            "data_hora_ultima_atualizacao": "2024-01-01T00:00:00Z",
            "grau": "1",
            "data_ajuizamento": "2023-12-01",
            "orgao_julgador": {"codigo": "1", "nome": "Vara"},
            "assuntos": ["Trabalho"],
            "movimentos": [
                {"nome": "Distribuído", "data_hora": "2024-01-01T00:00:00Z"}
            ]
        }
    ]
    resp = client.post(url, data, format='json')
    assert resp.status_code == 201
    assert Processo.objects.filter(numero_processo="0001").exists()
    assert resp.data[0]["numero_processo"] == "0001"

@pytest.mark.django_db
def test_deduplicar_nao_cria_existente():
    Processo.objects.create(
        numero_processo="0002",
        classe="B",
        tribunal="TRT6",
        data_hora_ultima_atualizacao="2024-01-01T00:00:00Z",
        grau="2",
        data_ajuizamento="2023-12-01"
    )
    client = APIClient()
    url = reverse('processoviewset-deduplicar')
    data = [
        {
            "numero_processo": "0002",
            "classe": "B",
            "tribunal": "TRT6",
            "data_hora_ultima_atualizacao": "2024-01-01T00:00:00Z",
            "grau": "2",
            "data_ajuizamento": "2023-12-01",
            "orgao_julgador": {"codigo": "2", "nome": "Vara"},
            "assuntos": ["Trabalho"],
            "movimentos": []
        }
    ]
    resp = client.post(url, data, format='json')
    assert resp.status_code == 201
    assert len(resp.data) == 0
