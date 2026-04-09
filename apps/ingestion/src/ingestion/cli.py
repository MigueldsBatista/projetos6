
import argparse

from ingestion.providers import APIDataProvider, DataProvider, FileDataProvider
from ingestion.utils import DATA_FOLDER


class IngestionParser:

    def __init__(self):
        parser = argparse.ArgumentParser(description="Ingestion pipeline CLI")
        parser.add_argument('--provider', choices=['file', 'api'], default='api', help='Tipo de provider de dados')
        parser.add_argument('--file-path', type=str, help='Caminho do arquivo JSON (para provider file)')
        parser.add_argument('--api-url', type=str, help='URL da API (para provider api)')
        parser.add_argument('--trigger', action='store_true', help='Disparar workers após ingestão')
        parser.add_argument(
            '--pending-pdf',
            action='store_true',
            help='Busca pendências de PDF na API e dispara o scraper para cada processo',
        )
        parser.add_argument(
            '--pending-api-url',
            type=str,
            default='http://localhost:8000/api/processos/nao_possuem_pdf/',
            help='Endpoint da API para listar processos sem PDF',
        )
        self.args = parser.parse_args()

    def get_cli_provider(self) -> DataProvider:
        provider: DataProvider | None = None

        if self.args.provider == 'file':
            file_path = self.args.file_path or DATA_FOLDER
            provider = FileDataProvider(file_path)
        else:
            api_url = self.args.api_url or "https://api-publica.datajud.cnj.jus.br/api_publica_trt6/_search"
            provider = APIDataProvider(api_url)

        return provider

    @property
    def trigger(self) -> bool:
        return bool(self.args.trigger)

    @property
    def pending_pdf(self) -> bool:
        return bool(self.args.pending_pdf)

    @property
    def pending_api_url(self) -> str:
        return str(self.args.pending_api_url)
