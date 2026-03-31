import requests
from shared.schemas.data_jud import ProcessoResumo


class ProcessSubmitter:
    def __init__(self, api_url: str = "http://localhost:8000/api/processos/bulk_create/"):
        self.api_url = api_url

    def submit(self, processos: list[dict]) -> list[ProcessoResumo] | None:
        try:
            response = requests.post(self.api_url, timeout=30, json=processos)
            response.raise_for_status()
            data = response.json()
            return [ProcessoResumo(**item) for item in data]
        except Exception:
            return None
