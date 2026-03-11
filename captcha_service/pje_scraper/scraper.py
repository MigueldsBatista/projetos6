"""Playwright-based scraper for pje.trt6.jus.br/consultaprocessual."""

import re
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import Page, Request, sync_playwright

from .captcha import CaptchaSolver
from .models import CaptchaSession, GrauInfo, ProcessInfo

PJE_BASE = "https://pje.trt6.jus.br/consultaprocessual"
SEARCH_URL = f"{PJE_BASE}/detalhe-processo/"

def search_url(num):
    return SEARCH_URL + num

class PjeScraper:
    """
    Scraper para o sistema PJe TRT-6.

    Usage:
        from pje_scraper import PjePipeline
        pipeline = PjePipeline()
        session = pipeline.resolve("0000573-11.2025.5.06.0021", grau="1")
        print(session.token_captcha)
    """

    def __init__(
        self,
        captcha_solver: CaptchaSolver,
        headless: bool = True,
        timeout_ms: int = 30_000,
    ):
        self.solver = captcha_solver
        self.headless = headless
        self.timeout_ms = timeout_ms

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #


    
    def get_token_captcha(
        self,
        numero_processo: str,
        grau: str = "1",
    ) -> CaptchaSession:
        """
        Executa o fluxo completo e retorna um CaptchaSession com tokenCaptcha.

        Args:
            numero_processo: ex. "0000573-11.2025.5.06.0021"
            grau: "1" (primeiro grau) ou "2" (segundo grau)

        Returns:
            CaptchaSession com token_desafio, token_captcha e demais dados.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context()
            page = context.new_page()
            page.set_default_timeout(self.timeout_ms)

            try:
                session = self._run(page, numero_processo, grau)
            finally:
                browser.close()

        return session

    def search_process(self, numero_processo: str) -> ProcessInfo:
        """
        Somente busca o processo e retorna os graus disponíveis (sem resolver captcha).
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context()
            page = context.new_page()
            page.set_default_timeout(self.timeout_ms)

            try:
                info = self._search(page, numero_processo)
            finally:
                browser.close()

        return info

    # ------------------------------------------------------------------ #
    #  Internal steps                                                      #
    # ------------------------------------------------------------------ #

    def _run(self, page: Page, numero_processo: str, grau: str) -> CaptchaSession:
        # Containers for intercepted values
        state: dict = {
            "token_desafio": None,
            "token_captcha": None,
            "processo_id": None,
        }

        # ---- Intercept requests to extract tokens ---- #
        def on_request(req: Request):
            url = req.url
            # Match requests like .../XXXXXXX?tokenDesafio=... or ?tokenCaptcha=...
            if "tokenDesafio=" in url:
                qs = parse_qs(urlparse(url).query)
                state["token_desafio"] = qs.get("tokenDesafio", [None])[0]
                # Extract processo ID from path: last numeric segment before '?'
                path_segment = urlparse(url).path.rstrip("/").split("/")[-1]
                if path_segment.isdigit():
                    state["processo_id"] = path_segment
            elif "tokenCaptcha=" in url:
                qs = parse_qs(urlparse(url).query)
                state["token_captcha"] = qs.get("tokenCaptcha", [None])[0]
                if state["processo_id"] is None:
                    path_segment = urlparse(url).path.rstrip("/").split("/")[-1]
                    if path_segment.isdigit():
                        state["processo_id"] = path_segment

        page.on("request", on_request)

        # Step 1 – Navigate to search page
        page.goto(SEARCH_URL, wait_until="networkidle")

        # Step 2 – Type process number and submit
        page.fill("#nrProcessoInput", numero_processo)
        page.click("#btnPesquisar")
        page.wait_for_load_state("networkidle")

        # Step 3 – Handle multi-grau selection
        process_info = self._detect_graus(page)

        if process_info.graus:
            # Multiple graus: click the requested one
            target_grau = self._find_grau(process_info.graus, grau)
            page.goto(target_grau.url, wait_until="networkidle")

        # Step 4 – Wait for captcha page
        page.wait_for_selector("#imagemCaptcha", timeout=self.timeout_ms)

        # Step 5 – Extract captcha image (base64 data URI from src attribute)
        captcha_src: str = page.get_attribute("#imagemCaptcha", "src") or ""
        captcha_text = self.solver.solve_base64(captcha_src)

        # Step 6 – Type answer and submit
        page.fill("#captchaInput", captcha_text)
        page.click("#btnEnviar")

        # Step 7 – Wait for tokenCaptcha to appear in a request
        self._wait_for_token_captcha(page, state)

        if state["token_captcha"] is None:
            raise RuntimeError(
                "tokenCaptcha not captured. Possible wrong captcha answer or page error."
            )
        if state["token_desafio"] is None:
            raise RuntimeError("tokenDesafio not captured from network requests.")

        return CaptchaSession(
            numero_processo=numero_processo,
            grau=grau,
            processo_id=state["processo_id"] or "",
            token_desafio=state["token_desafio"],
            token_captcha=state["token_captcha"],
            captcha_text=captcha_text,
        )

    def _search(self, page: Page, numero_processo: str) -> ProcessInfo:
        page.goto(SEARCH_URL, wait_until="networkidle")
        page.fill("#nrProcessoInput", numero_processo)
        page.click("#btnPesquisar")
        page.wait_for_load_state("networkidle")
        return self._detect_graus(page)

    def _detect_graus(self, page: Page) -> ProcessInfo:
        """
        Detecta se a página mostra múltiplos graus (links 1°/2° Grau) ou
        redireciona diretamente para o processo.
        """
        # Check for grau links: "PJe 1° Grau" / "PJe 2° Grau"
        # The "mais de um grau" page shows links like href="https://pje.trt6.jus.br/primeirograu"
        # but the consultaprocessual app shows grau selection inside its own router.
        # We look for links containing "primeirograu" or "segundograu" in their href,
        # or for elements that contain the text "1° Grau" / "2° Grau".
        graus = []
        grau_links = page.query_selector_all("a[href*='primeirograu'], a[href*='segundograu']")
        for link in grau_links:
            href = link.get_attribute("href") or ""
            text = (link.inner_text() or "").strip()
            if "primeirograu" in href:
                graus.append(GrauInfo(grau="1", label=text or "PJe 1° Grau", url=href))
            elif "segundograu" in href:
                graus.append(GrauInfo(grau="2", label=text or "PJe 2° Grau", url=href))

        # Fallback: Angular router-based grau selection (internal links)
        if not graus:
            grau_links_ng = page.query_selector_all("a[href*='detalhe-processo']")
            for link in grau_links_ng:
                href = link.get_attribute("href") or ""
                text = (link.inner_text() or "").strip()
                # Try to infer grau from text
                g = "1" if "1" in text else ("2" if "2" in text else "?")
                graus.append(GrauInfo(grau=g, label=text, url=href))

        # Extract processo number from URL or title
        current_url = page.url
        numero_match = re.search(r"(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})", current_url)
        numero = numero_match.group(1) if numero_match else ""

        return ProcessInfo(
            numero=numero,
            graus=graus,
            single_url=current_url if not graus else None,
        )

    def _find_grau(self, graus: list[GrauInfo], grau: str) -> GrauInfo:
        for g in graus:
            if g.grau == grau:
                return g
        # Fallback: first available
        return graus[0]

    def _wait_for_token_captcha(self, page: Page, state: dict, max_wait_ms: int = 15_000) -> None:
        """
        Aguarda até o tokenCaptcha ser capturado via request interception,
        ou até um timeout.
        """
        import time
        deadline = time.time() + max_wait_ms / 1000
        while time.time() < deadline:
            if state["token_captcha"] is not None:
                return
            page.wait_for_timeout(300)
        if state["token_captcha"] is None:
            raise TimeoutError(
                f"Timeout waiting for tokenCaptcha after {max_wait_ms}ms. "
                "The captcha may have been solved incorrectly."
            )


