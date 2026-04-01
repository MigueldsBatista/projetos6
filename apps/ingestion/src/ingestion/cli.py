
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
