"""
Ponto de entrada principal do pje-scraper.

Pré-requisitos:
  pip install -e captcha_service/
  playwright install chromium

Uso:
    python main.py 0000573-11.2025.5.06.0021
    python main.py 0000573-11.2025.5.06.0021 1 --no-headless
"""

import json
import sys

from pje_scraper import PjePipeline


def main():
    numero = sys.argv[1] if len(sys.argv) > 1 else "0000573-11.2025.5.06.0021"
    grau = sys.argv[2] if len(sys.argv) > 2 else "1"
    headless = "--no-headless" not in sys.argv

    print(f"[*] Buscando processo: {numero} | Grau: {grau}")

    pipeline = PjePipeline(headless=headless)

    try:
        session = pipeline.resolve(numero, grau=grau)
    except Exception as e:
        print(f"[!] Erro: {e}")
        sys.exit(1)

    print("\n[✓] Captcha resolvido!")
    print(f"    Processo ID  : {session.processo_id}")
    print(f"    Captcha texto: {session.captcha_text}")
    print(f"    tokenDesafio : {session.token_desafio}")
    print(f"    tokenCaptcha : {session.token_captcha}")

    print("\n[*] Buscando documentos do processo...")
    try:
        resp = pipeline.fetch_with_token(session)
        content_type = resp.headers.get("content-type", "")
        print(f"    Status       : {resp.status_code}")
        if "application/json" in content_type:
            print(f"    Body (JSON)  : {json.dumps(resp.json(), indent=2, ensure_ascii=False)[:500]}")
        elif "application/pdf" in content_type:
            out = f"{session.numero_processo.replace('/', '_')}.pdf"
            with open(out, "wb") as f:
                f.write(resp.content)
            print(f"    PDF salvo em : {out}")
        else:
            print(f"    Body (raw)   : {resp.text[:300]}")
    except Exception as e:
        print(f"[!] Erro ao buscar documentos: {e}")


if __name__ == "__main__":
    main()
