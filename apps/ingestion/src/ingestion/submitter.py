import requests
from shared.logger import get_logger
from shared.schemas.data_jud import ProcessoResumo

logger = get_logger("submitter")

class ProcessSubmitter:
    def __init__(self, api_url: str = "http://localhost:8000/api/processos/deduplicar/"):
        self.api_url = api_url

    def submit(self, processos: list[dict]) -> list[ProcessoResumo] | None:
        try:
            response = requests.post(self.api_url, timeout=30, json=processos)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Resposta da API: {data}")
            return [ProcessoResumo(**item) for item in data]
        except Exception as e:
            logger.error(f"Failed to submit processes: {e}")
            return None
