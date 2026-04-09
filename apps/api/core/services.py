
from collections.abc import Mapping, Sequence

from django.db.models import Q
from shared.s3_client import get_s3_client

from core.models.processo import Processo

PDF_BUCKET_NAME = "pje-documents"


class ProcessoSemPdfLookupError(Exception):
    """Raised when pending PDF lookup cannot be completed."""


def _normalize_grau(grau: str) -> str:
    raw = (grau or "").strip().upper()
    if raw.startswith("G") and len(raw) > 1:
        return raw[1:]
    return raw


def _s3_object_key(numero_processo: str, grau: str) -> str:
    return f"{numero_processo}_{_normalize_grau(grau)}.pdf"


def _s3_object_exists(client, bucket_name: str, object_name: str) -> bool:
    objects = client.list_objects(bucket_name, prefix=object_name, recursive=True)
    return any(getattr(item, "object_name", "") == object_name for item in objects)


def filtrar_processos_faltantes(
    dados_entrada: Sequence[dict],
) -> list[dict]:
    # Deduplica o lote por chave unica do modelo para evitar conflitos no mesmo request.
    # Em caso de repeticao da mesma chave, mantem o item mais recente.
    deduplicado_por_chave: dict[tuple[str, str, str], dict] = {}
    for item in dados_entrada:
        chave = (
            item.get("numero_processo", ""),
            item.get("tribunal", ""),
            item.get("grau", ""),
        )

        existente = deduplicado_por_chave.get(chave)
        if existente is None:
            deduplicado_por_chave[chave] = item
            continue

        data_nova = item.get("data_hora_ultima_atualizacao")
        data_existente = existente.get("data_hora_ultima_atualizacao")
        if data_nova and (data_existente is None or data_nova > data_existente):
            deduplicado_por_chave[chave] = item

    itens_deduplicados = list(deduplicado_por_chave.values())

    numeros_entrada: list[str] = [item["numero_processo"] for item in itens_deduplicados]

    if not numeros_entrada:
        return []

    processos_no_banco = Processo.objects.filter(numero_processo__in=numeros_entrada).values(
        "numero_processo",
        "tribunal",
        "grau",
    )

    chaves_banco: Mapping[tuple[str, str, str], bool] = {
        (item["numero_processo"], item["tribunal"], item["grau"]): True
        for item in processos_no_banco
    }

    def precisa_de_processamento(item: dict) -> bool:
        chave = (
            item.get("numero_processo", ""),
            item.get("tribunal", ""),
            item.get("grau", ""),
        )
        return chave not in chaves_banco

    return [item for item in itens_deduplicados if precisa_de_processamento(item)]


def listar_processos_nao_possuem_pdf() -> list[Processo]:
    client = get_s3_client()
    candidatos = Processo.objects.filter(Q(pdf_url__isnull=True) | Q(pdf_url="")).only(
        "numero_processo",
        "grau",
        "pdf_url",
    )

    pendentes: list[Processo] = []
    for processo in candidatos:
        object_name = _s3_object_key(processo.numero_processo, processo.grau)
        try:
            exists = _s3_object_exists(client, PDF_BUCKET_NAME, object_name)
        except Exception as exc:
            raise ProcessoSemPdfLookupError("Falha ao consultar objetos PDF no S3.") from exc

        if not exists:
            pendentes.append(processo)

    return pendentes
