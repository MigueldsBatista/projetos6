
import json
from typing import Any

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from shared.schemas.resumo_ia import ProcessoAnalise


def extract_text_from_pdf(pdf_path):
    with open(pdf_path) as f:
        return f.read()

def save_response(result: Any, path: str = "result.json"):
    with open(path, "w", encoding="utf-8") as f:
        if hasattr(result, "model_dump"):
            json.dump(result.model_dump(), f, ensure_ascii=False, indent=2)
        elif isinstance(result, dict):
            json.dump(result, f, ensure_ascii=False, indent=2)
        else:
            f.write(str(result))

def main():
    pdf_path = "output/mock.md"
    pdf_text = extract_text_from_pdf(pdf_path)

    explanation = """
    Você receberá o texto extraído de um PDF de consulta de processos do TRT6 (Tribunal Regional do Trabalho da 6ª Região).

    Extraia os seguintes campos e retorne APENAS um JSON com a estrutura abaixo. Siga as regras para cada campo:

    - numero_processo: Extraia o número do processo no formato CNJ (ex: 0000256-48.2025.5.06.0171).
    - tribunal: Sempre "TRT6".
    - classe_nome: Extraia o nome da classe processual (ex: "Ação Trabalhista - Rito Sumaríssimo").
    - orgao_julgador_nome: Nome da vara ou órgão julgador (ex: "1ª Vara do Trabalho do Cabo").
    - data_ajuizamento: Data em que o processo foi ajuizado, formato YYYY-MM-DD (ex: 2025-04-15).
    - tempo_tramitacao: Tempo total de tramitação do processo, calculado a partir da data de ajuizamento até a data da última decisão, em dias.
    - resumo: Resuma em 2-3 frases qual foi motivo de abertura da ação, e objetivo esperado a ser alcançado, usando informações do texto, incluindo pedidos, contexto e partes envolvidas.
    - tipo_ato_principal: Classifique como um dos enums: acordo_homologado, sentenca, acordao, despacho, outro. Use palavras-chave como "ACORDO HOMOLOGADO", "SENTENÇA", "DESPACHO".
    - decisao: Resuma em 2-3 frases a decisão principal, citando valores, partes e resultado.
    - palavras_chave: Liste pelo menos 5 palavras-chave relevantes do processo, extraídas do texto que consigam classificar o processo e encontrar outros similares e liste mais 5 palavras chaves relacionadas ao desfecho
    - status: Classifique como um dos enums: arquivado, acordo_homologado, sentenciado, em_andamento. Use regras: "arquivem-se" => arquivado; "acordo homologado" => acordo_homologado; "sentença" sem arquivamento => sentenciado; senão em_andamento.
    - desfecho: Classifique como um dos enums: acordo_favoravel, sentenca_procedente, sentenca_parcialmente_procedente, sentenca_improcedente, extinta, arquivado_sem_decisao, outro. Use palavras-chave e contexto.
    - resultado_reclamante: Classifique como um dos enums: ganhou, ganhou_parcial, perdeu, sem_decisao. Use o desfecho para inferir.
    - valor_causa: Valor monetário da causa, extraído do texto (ex: 31399.70).
    - custas_valor_total: Valor total das custas, se houver.

    Se algum campo não estiver presente, preencha com null.
    """

    llm = ChatOpenAI(
        base_url="http://172.26.192.1:1234/v1",
        api_key="lm-studio",
        model_name="google/gemma-3-4b"
    )

    agent = create_agent(
        model=llm,
        response_format=ProcessoAnalise,
    )

    messages = [
        {"role": "system", "content": explanation},
        {"role": "user", "content": f"Texto extraído do PDF:\n{pdf_text}"}
    ]

    response = agent.invoke({"messages": messages})

    if "structured_response" in response:
        save_response(response["structured_response"])

if __name__ == "__main__":
    main()
