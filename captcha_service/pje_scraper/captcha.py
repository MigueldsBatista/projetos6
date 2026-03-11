import base64

import ddddocr


class CaptchaSolver:
    """
    Resolve captchas usando a biblioteca ddddocr diretamente (sem serviço HTTP).
    """

    def __init__(self):
        self._ocr = ddddocr.DdddOcr(show_ad=False)

    def solve(self, image_bytes: bytes) -> str:
        """Resolve um captcha a partir dos bytes da imagem."""
        return self._ocr.classification(image_bytes)

    def solve_base64(self, b64_image: str) -> str:
        """Resolve um captcha a partir de uma string base64 (com ou sem prefixo data:image/...)."""
        if "base64," in b64_image:
            b64_image = b64_image.split("base64,", 1)[1].strip()
        return self.solve(base64.b64decode(b64_image))
