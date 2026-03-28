import json
import re
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "r") as f:
        return f.read()

def extract_json_from_response(text):
    match = re.search(r"```json\\s*(.*?)\\s*```", text, re.DOTALL)
    if not match:
        match = re.search(r"```\\s*(.*?)\\s*```", text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        json_str = text
    json_str = json_str.replace("\\n", "\n")
    return json_str


def save_response(result: Any):
    with open("result.json", "w", encoding="utf-8") as f:
        if isinstance(result, dict):
            json.dump(result, f, ensure_ascii=False, indent=2)
        else:
            f.write(str(result))
def main():
    pdf_path = "output/mock.md"
    pdf_text = extract_text_from_pdf(pdf_path)

    explanation = """
    Você receberá o texto extraído de um PDF de consulta de processos do TRT6 (Tribunal Regional do Trabalho da 6ª Região).
    Extraia os seguintes campos e retorne um JSON com a estrutura abaixo.

    - numero_processo: número do processo
    - tribunal: tribunal responsável (ex: TRT6)
    - classe_nome: nome da classe processual (ex: Ação Trabalhista - Rito Sumaríssimo)
    - orgao_julgador_nome: nome da vara ou órgão julgador
    - data_ajuizamento: data em que o processo foi ajuizado (formato YYYY-MM-DD)
    - resumo_causa: resumo do detalhado do motivo da ação
    - tipo_ato_principal: tipo do principal ato processual (ex: acordo_homologado)
    - decisao_resumo: resumo da decisão principal
    - palavras_chave_processo: lista de palavras-chave do processo (minimo 5)
    - status_processo: status atual do processo (ex: arquivado, em andamento)
    - desfecho: desfecho principal (ex: acordo_favoravel)
    - resultado_reclamante: resultado para o reclamante (ex: ganhou, perdeu, parcial)
    - palavras_chave_desfecho: lista de palavras-chave do desfecho (minimo 5)
    - valor_causa: valor da causa (float)
    - custas_valor_total: valor total das custas (float)
    - custas_percentual: percentual das custas (float)

    Se algum campo não estiver presente, preencha com null ou valor vazio.
    Retorne apenas o JSON extraído.
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", explanation),
        ("user", f"Texto extraído do PDF:\n{pdf_text}")
    ])

    llm = ChatOpenAI(
        base_url="http://172.26.192.1:1234/v1",
        api_key="lm-studio",
        model_name="google/gemma-3-4b"
    )

    chain = prompt | llm
    response = chain.invoke({"pdf_text": pdf_text})

    json_str = extract_json_from_response(response.content)
    try:
        result = json.loads(json_str)
    except Exception:
        result = json_str

    save_response(result)
    print(json_str)

if __name__ == "__main__":
    main()