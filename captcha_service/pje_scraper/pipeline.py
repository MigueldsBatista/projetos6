"""
Pipeline de alto nível: dado um número de processo, retorna o tokenCaptcha
pronto para uso em requisições à API do PJe.
"""

import httpx

from .captcha import CaptchaSolver
from .models import CaptchaSession
from .scraper import PjeScraper

PJE_BFF_BASE = "https://pje.trt6.jus.br/pje-bff/consultaprocessual/api"


class PjePipeline:
    """
    Orquestra: busca → seleção de grau → resolução de captcha → tokenCaptcha.

    Usage:
        from pje_scraper import PjePipeline
        pipeline = PjePipeline()
        session = pipeline.resolve("0000573-11.2025.5.06.0021", grau="1")
        docs = pipeline.fetch_with_token(session)
    """

    def __init__(self, headless: bool = True, timeout_ms: int = 30_000):
        solver = CaptchaSolver()
        self.scraper = PjeScraper(solver, headless=headless, timeout_ms=timeout_ms)

    def resolve(self, numero_processo: str, grau: str = "1") -> CaptchaSession:
        """
        Executa o pipeline completo e retorna um CaptchaSession com tokenCaptcha.

        Raises:
            RuntimeError: Se o tokenCaptcha não foi obtido.
            TimeoutError: Se a página demorou demais para responder.
        """
        return self.scraper.get_token_captcha(numero_processo, grau=grau)

    def fetch_with_token(
        self,
        session: CaptchaSession,
        extra_params: dict | None = None,
    ) -> httpx.Response:
        """
        Faz uma requisição à API do PJe usando o tokenCaptcha obtido.

        Note:
            A URL exata deve ser confirmada via DevTools (Network tab) no navegador.
            Este método usa o padrão observado: GET /{processo_id}?tokenCaptcha={token}
        """
        params = {"tokenCaptcha": session.token_captcha}
        if extra_params:
            params.update(extra_params)

        url = f"{PJE_BFF_BASE}/{session.processo_id}"
        resp = httpx.get(url, params=params, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        return resp


def main() -> None:
    """Entry point do comando 'pje-scraper' instalado via pyproject.toml."""
    import sys

    numero = sys.argv[1] if len(sys.argv) > 1 else "0000573-11.2025.5.06.0021"
    grau = sys.argv[2] if len(sys.argv) > 2 else "1"
    headless = "--no-headless" not in sys.argv

    pipeline = PjePipeline(headless=headless)
    session = pipeline.resolve(numero, grau=grau)

    print(f"processo_id  : {session.processo_id}")
    print(f"grau         : {session.grau}")
    print(f"captcha_text : {session.captcha_text}")
    print(f"tokenDesafio : {session.token_desafio}")
    print(f"tokenCaptcha : {session.token_captcha}")
