import os

import requests
from shared.logger import get_logger
from shared.schemas.data_jud import ProcessoResumo

logger = get_logger("submitter")


def _is_log_errors_enabled() -> bool:
    return os.getenv("LOG_ERRORS", "false").strip().lower() in {"1", "true", "yes", "on"}


def _sample_process_numbers(processos: list[dict], limit: int = 3) -> list[str]:
    sample: list[str] = []
    for processo in processos[:limit]:
        numero = processo.get("numero_processo")
        if numero is not None:
            sample.append(str(numero))
    return sample


class ProcessSubmitter:
    def __init__(
        self,
        api_url: str = "http://localhost:8000/api/processos/deduplicar/",
        pending_api_url: str = "http://localhost:8000/api/processos/nao_possuem_pdf/",
    ):
        self.api_url = api_url
        self.pending_api_url = pending_api_url

    def submit(self, processos: list[dict]) -> list[ProcessoResumo] | None:
        try:
            response = requests.post(self.api_url, timeout=30, json=processos)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Resposta da API: {data}")
            return [ProcessoResumo(**item) for item in data]
        except requests.exceptions.HTTPError as exc:
            response = exc.response
            if _is_log_errors_enabled() and response is not None:
                logger.error(
                    "Failed to submit processes: %s | status=%s | batch_size=%s | numeros=%s | response=%s",
                    exc,
                    response.status_code,
                    len(processos),
                    _sample_process_numbers(processos),
                    response.text,
                )
            else:
                logger.error(f"Failed to submit processes: {exc}")
            return None
        except requests.exceptions.RequestException as exc:
            logger.error(f"Failed to submit processes due to request error: {exc}")
            return None
        except Exception as exc:
            logger.error(f"Failed to submit processes: {exc}")
            return None

    def fetch_pending_pdf(self) -> list[ProcessoResumo] | None:
        try:
            response = requests.get(self.pending_api_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Resposta de pendencias PDF: {data}")
            return [ProcessoResumo(**item) for item in data]
        except requests.exceptions.HTTPError as exc:
            response = exc.response
            if _is_log_errors_enabled() and response is not None:
                logger.error(
                    "Failed to fetch pending PDFs: %s | status=%s | response=%s",
                    exc,
                    response.status_code,
                    response.text,
                )
            else:
                logger.error(f"Failed to fetch pending PDFs: {exc}")
            return None
        except requests.exceptions.RequestException as exc:
            logger.error(f"Failed to fetch pending PDFs due to request error: {exc}")
            return None
        except Exception as exc:
            logger.error(f"Failed to fetch pending PDFs: {exc}")
            return None
