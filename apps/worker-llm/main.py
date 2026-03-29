
import json
from enum import StrEnum
from typing import Any

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from openai import BaseModel
from pydantic import Field


class TipoAtoPrincipal(StrEnum):
    ACORDO_HOMOLOGADO = "acordo_homologado"
    SENTENCA = "sentenca"
    ACORDAO = "acordao"
    DESPACHO = "despacho"
    OUTRO = "outro"

class StatusProcesso(StrEnum):
    ARQUIVADO = "arquivado"
    ACORDO_HOMOLOGADO = "acordo_homologado"
    SENTENCIADO = "sentenciado"
    EM_ANDAMENTO = "em_andamento"

class Desfecho(StrEnum):
    ACORDO_FAVORAVEL = "acordo_favoravel"
    SENTENCA_PROCEDENTE = "sentenca_procedente"
    SENTENCA_PARCIALMENTE_PROCEDENTE = "sentenca_parcialmente_procedente"
    SENTENCA_IMPROCEDENTE = "sentenca_improcedente"
    EXTINTA = "extinta"
    ARQUIVADO_SEM_DECISAO = "arquivado_sem_decisao"
    OUTRO = "outro"

class ResultadoReclamante(StrEnum):
    GANHOU = "ganhou"
    GANHOU_PARCIAL = "ganhou_parcial"
    PERDEU = "perdeu"
    SEM_DECISAO = "sem_decisao"


class ProcessoDetalhado(BaseModel):
    numero_processo: str | None = Field(default=None, description="Número do processo")
    tribunal: str | None = Field(default=None, description="Tribunal responsável")
    classe_nome: str | None = Field(default=None, description="Nome da classe processual")
    orgao_julgador_nome: str | None = Field(default=None, description="Nome da vara ou órgão julgador")
    data_ajuizamento: str | None = Field(default=None, description="Data em que o processo foi ajuizado")
    tempo_tramitacao: int | None = Field(default=None, description="Tempo total de tramitação do processo, em dias")
    resumo_causa: str | None = Field(default=None, description="Resumo do detalhado do motivo da ação")
    tipo_ato_principal: TipoAtoPrincipal | None = Field(default=None, description="Tipo do principal ato processual")
    decisao_resumo: str | None = Field(default=None, description="Resumo da decisão principal")
    palavras_chave_processo: list[str | None] = Field(default=None, description="Lista de palavras-chave do processo", min_length=5)
    status_processo: StatusProcesso | None = Field(default=None, description="Status atual do processo")
    desfecho: Desfecho | None = Field(default=None, description="Desfecho principal")
    resultado_reclamante: ResultadoReclamante | None = Field(default=None, description="Resultado para o reclamante")
    palavras_chave_desfecho: list[str | None] = Field(default=None, description="Lista de palavras-chave do desfecho", min_length=5)
    valor_causa: float | None = Field(default=None, description="Valor da causa")
    custas_valor_total: float | None = Field(default=None, description="Valor total das custas")
    custas_percentual: float | None = Field(default=None, description="Percentual das custas")


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
    - resumo_causa: Resuma em 2-3 frases qual foi motivo de abertura da ação, e objetivo esperado a ser alcançado, usando informações do texto, incluindo pedidos, contexto e partes envolvidas.
    - tipo_ato_principal: Classifique como um dos enums: acordo_homologado, sentenca, acordao, despacho, outro. Use palavras-chave como "ACORDO HOMOLOGADO", "SENTENÇA", "DESPACHO".
    - decisao_resumo: Resuma em 2-3 frases a decisão principal, citando valores, partes e resultado.
    - palavras_chave_processo: Liste pelo menos 5 palavras-chave relevantes do processo, extraídas do texto que consigam classificar o processo e encontrar outros similares
    - status_processo: Classifique como um dos enums: arquivado, acordo_homologado, sentenciado, em_andamento. Use regras: "arquivem-se" => arquivado; "acordo homologado" => acordo_homologado; "sentença" sem arquivamento => sentenciado; senão em_andamento.
    - desfecho: Classifique como um dos enums: acordo_favoravel, sentenca_procedente, sentenca_parcialmente_procedente, sentenca_improcedente, extinta, arquivado_sem_decisao, outro. Use palavras-chave e contexto.
    - resultado_reclamante: Classifique como um dos enums: ganhou, ganhou_parcial, perdeu, sem_decisao. Use o desfecho para inferir.
    - palavras_chave_desfecho: Liste pelo menos 5 palavras/frases do texto que justificam o desfecho, elas devem ser capazes de classificar o desfecho e encontrar outros similares.
    - valor_causa: Valor monetário da causa, extraído do texto (ex: 31399.70).
    - custas_valor_total: Valor total das custas, se houver.
    - custas_percentual: Percentual das custas, se houver.

    Se algum campo não estiver presente, preencha com null.

    """

    llm = ChatOpenAI(
        base_url="http://172.26.192.1:1234/v1",
        api_key="lm-studio",
        model_name="google/gemma-3-4b"
    )

    agent = create_agent(
        model=llm,
        response_format=ProcessoDetalhado,
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
