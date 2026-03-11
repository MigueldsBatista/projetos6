from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GrauInfo:
    """Representa uma instância (grau) de um processo."""
    grau: str               # "1", "2", etc.
    label: str              # "PJe 1° Grau", "PJe 2° Grau"
    url: str                # URL do link de acesso ao grau
    processo_id: Optional[str] = None  # ID interno extraído após navegar


@dataclass
class ProcessInfo:
    """Resultado da busca por número de processo."""
    numero: str
    graus: list[GrauInfo] = field(default_factory=list)
    single_url: Optional[str] = None   # Set when there's only one grau (no selection needed)


@dataclass
class CaptchaSession:
    """Estado de uma sessão de captcha resolvida."""
    numero_processo: str
    grau: str
    processo_id: str          # ID interno do processo no grau selecionado
    token_desafio: str        # Token do desafio captcha
    token_captcha: str        # Token resultante após resolver o captcha
    captcha_text: str         # Texto reconhecido pelo OCR
