# Especificacao de dados TRT6 (JSON DataJud + PDF integra)

## 1) Exemplo de dado final (sample)
```json
{
  "processo_numero_cnj": "0000256-48.2025.5.06.0171",
  "processo_id_datajud": "TRT6_G1_00002564820255060171",
  "tribunal": "TRT6",
  "grau": "G1",
  "classe_nome": "Acao Trabalhista - Rito Sumarissimo",
  "orgao_julgador_nome": "1a Vara do Trabalho do Cabo",
  "data_ajuizamento": "2025-04-15",
  "resumo_causa": "ABC what happened"
  "tipo_ato_principal": "acordo_homologado",
  "decisao_resumo": "Acordo homologado com quitacao geral e previsao de multa por inadimplencia.",
  "palavras_chave_processo": ["pagamento de salario", "acordo judicial", "quitacao geral", "multa por inadimplencia"],
  "status_processo": "arquivado",
  "desfecho": "acordo_favoravel",
  "resultado_reclamante": "ganhou",
  "palavras_chave_desfecho": ["ACORDO HOMOLOGADO", "CONCILIACAO", "pagara ao reclamante", "R$ 2.500,00"],
  "valor_causa": 31399.70,
  "valor_acordo_total": 2500.00,
  "valor_pago_reclamante": 2500.00,
  "valor_pago_advogado": 750.00,
  "custas_valor": 50.00,
  "custas_percentual": 2.00,
  "prazo_pagamento_texto": "parcela unica ate 30.07.2025",
  "data_sentenca_pdf": "2026-01-16",
  "data_arquivamento_pdf": "2026-01-16",
}
```

## 2) Dicionario campo a campo: referencia, descricao e como obter

Legenda de fonte:
- DataJud = JSON retornado no formato hits.hits[*]._source
- PDF = texto extraido do arquivo de integra (via pypdf)
- Derivado = calculado a partir de DataJud e/ou PDF

| Campo | Descricao (o que e) | Fonte primaria | Referencia exata | Como obter (regra) |
|---|---|---|---|---|
| processo_numero_cnj | Numero CNJ unico do processo para identificacao logica. | DataJud | _source.numeroProcesso | Ler string e normalizar para formato CNJ com mascara quando necessario. |
| processo_id_datajud | Identificador tecnico do processo no retorno da API DataJud. | DataJud | _source.id | Copiar id tecnico retornado pela API. |
| tribunal | Sigla do tribunal de origem do processo. | DataJud | _source.tribunal | Copiar valor literal. |
| grau | Grau de jurisdicao do processo (G1 ou G2). | DataJud | _source.grau | Copiar valor literal (G1/G2). |
| classe_codigo | Codigo numerico da classe processual. | DataJud | _source.classe.codigo | Copiar inteiro. |
| classe_nome | Nome textual da classe processual. | DataJud | _source.classe.nome | Copiar texto. |
| orgao_julgador_codigo | Codigo do orgao julgador responsavel. | DataJud | _source.orgaoJulgador.codigo | Copiar codigo numerico/string. |
| orgao_julgador_nome | Nome do orgao julgador responsavel. | DataJud | _source.orgaoJulgador.nome | Copiar texto. |
| data_ajuizamento | Data de distribuicao/ajuizamento do processo. | DataJud | _source.dataAjuizamento | Converter AAAAMMDDhhmmss para data ISO (AAAA-MM-DD). |
| data_ultima_atualizacao_datajud | Momento da ultima atualizacao do processo na fonte. | DataJud | _source.dataHoraUltimaAtualizacao | Converter para datetime ISO UTC. |
| data_ato_principal_pdf | Data do principal ato decisorio identificado no PDF. | PDF | Texto do ato principal no PDF | Detectar bloco mais relevante (acordo/sentenca/acordao/despacho final) e extrair data do bloco. |
| data_sentenca_pdf | Data da sentenca quando houver sentenca no inteiro teor. | PDF | Bloco com palavra "SENTENCA" | Encontrar sentenca e extrair data da assinatura ou data textual do bloco. |
| data_arquivamento_pdf | Data do ato que determina o arquivamento dos autos. | PDF | Trechos com "arquivem-se" | Se houver comando de arquivamento, usar data do ato correspondente. |
| reclamante_nome | Nome da parte autora da reclamacao trabalhista. | PDF | Linha "RECLAMANTE:" | Regex apos marcador "RECLAMANTE:". |
| reclamado_nome | Nome da parte re no processo trabalhista. | PDF | Linha "RECLAMADO:" ou "RECLAMADO(A):" | Regex apos marcador de parte passiva. |
| assuntos | Lista de temas juridicos associados ao processo. | DataJud | _source.assuntos[*].nome | Mapear array de objetos para array de strings. |
| tipo_ato_principal | Classificacao do ato principal (despacho, acordo, sentenca, acordao, outro). | Derivado | PDF + movimentos DataJud | Classificar por palavras-chave: ACORDO HOMOLOGADO, SENTENCA, ACORDAO, DESPACHO. |
| decisao_resumo | Resumo textual curto do conteudo decisorio principal. | PDF | Bloco textual do ato principal | Resumir em 1-3 frases a partir do bloco identificado como principal. |
| status_processo | Situacao processual consolidada para consulta e analise. | Derivado | PDF + movimentos DataJud | Regras: "arquivem-se" => arquivado; "acordo homologado" => acordo_homologado; "sentenca" sem arquivamento => sentenciado; senao em_andamento. |
| desfecho | Classificacao final do resultado: acordo favoravel, sentenca procedente, improcedente, extinta, etc. | Derivado | PDF (blocos de ACORDO, SENTENCA, ACORDAO) | Usar padroes de palavras-chave conforme secao 4.1 para mapear a cada enum. |
| resultado_reclamante | Resumo binario/ternario: ganhou, ganhou_parcial, perdeu, sem_decisao. | Derivado | Campo "desfecho" mapeado para resultado. | ganhou => acordo favoravel ou sentenca procedente; perdeu => improcedente; ganhou_parcial => parcialmente procedente; sem_decisao => extinta ou em andamento. |
| palavras_chave_desfecho | Array de strings encontradas no PDF que levaram a classificacao do desfecho. | PDF | Blocos de ACORDO/SENTENCA/ACORDAO | Capturar termos como "ACORDO HOMOLOGADO", "CONCILIACAO", "procedente", "improcedente", "pagara ao reclamante", "R$ X", etc. |
| palavras_chave_processo | Array de temas juridicos e fatos relevantes do processo para indexacao semantica. | Derivado | Chunks relevantes do PDF integra + assuntos do DataJud | Extrair via RAG com recuperacao semantica dos trechos mais representativos e normalizar para termos canonicos (ex: "pagamento de salario", "verbas rescisorias", "jornada de trabalho", "acordo judicial", "quitacao geral", "inadimplencia"). |
| valor_causa | Valor economico atribuido a causa no processo. | PDF | Linha "Valor da causa" | Regex monetaria apos marcador "Valor da causa:" e normalizar para decimal. |
| valor_acordo_total | Valor total pactuado no acordo homologado. | PDF | Bloco "CONCILIACAO"/"ACORDO HOMOLOGADO" | Capturar valor total do acordo quando expresso como importancia total. |
| valor_pago_reclamante | Valor financeiro destinado ao reclamante no acordo/decisao. | PDF | Bloco de pagamento ao reclamante | Regex em frase "pagara ao reclamante ... R$ X". |
| valor_pago_advogado | Valor financeiro destinado ao advogado do reclamante. | PDF | Bloco de pagamento ao advogado | Regex em frase "pagara ao advogado ... R$ X". |
| custas_valor | Valor absoluto das custas processuais. | PDF | Linha com "Custas ... R$" | Regex de valor monetario apos marcador "Custas". |
| custas_percentual | Percentual de custas aplicado no ato. | PDF | Linha com "Custas" e "%" | Regex de percentual no mesmo trecho das custas. |
| raw_pdf_texto | Conteudo bruto do texto integral extraido do PDF. | PDF | Texto extraido integral | Persistir texto bruto extraido do PDF. |

## 9) Evidencias concretas no caso exemplo (0000256-48.2025.5.06.0171)

Trechos no texto extraido em captcha_service/documents/00002564820255060171_integra_http_extracted.txt:
- "Valor da causa: R$ 31.399,70" -> valor_causa
- "RECLAMANTE: LEANDRO ..." -> reclamante_nome
- "RECLAMADO: ECAM ..." -> reclamado_nome
- "ACORDO HOMOLOGADO." -> tipo_ato_principal/status_processo/desfecho/resultado_reclamante
- "A esta altura as partes resolveram conciliar" -> palavras_chave_desfecho
- "pagara ao reclamante ... R$ 2.500,00" -> valor_pago_reclamante + palavras_chave_desfecho
- "Custas ... R$ 50,00, 2%" -> custas_valor/custas_percentual
- "Multa de 100% ..." -> multa_inadimplencia_percentual
- "SENTENCA" + "arquivem-se" + data "16 de janeiro de 2026" -> data_sentenca_pdf/data_arquivamento_pdf

Exemplos recomendados de palavras-chave para indexacao via RAG:
- palavras_chave_processo: ["pagamento de salario", "rescisao indireta", "verbas rescisorias", "jornada de trabalho", "acordo judicial", "quitacao geral", "inadimplencia"]
- palavras_chave_desfecho (acordo_favoravel): ["ACORDO HOMOLOGADO", "CONCILIACAO", "pagara ao reclamante", "quitacao geral", "resolucao de merito"]
- palavras_chave_desfecho (sentenca_procedente): ["julgo procedente", "condeno a reclamada", "procedencia dos pedidos"]
- palavras_chave_desfecho (sentenca_parcialmente_procedente): ["julgo parcialmente procedente", "procedente em parte", "deferido em parte"]
- palavras_chave_desfecho (sentenca_improcedente): ["julgo improcedente", "indeferidos os pedidos", "rejeito os pedidos"]
- palavras_chave_desfecho (sentenca_extinta/arquivado_sem_decisao): ["extingo o processo", "sem resolucao de merito", "arquivem-se os autos"]

Referencias no JSON DataJud (estrutura):
```json
hits.hits[0]._source.numeroProcesso
hits.hits[0]._source.id
hits.hits[0]._source.tribunal
hits.hits[0]._source.grau
hits.hits[0]._source.classe.codigo
hits.hits[0]._source.classe.nome
hits.hits[0]._source.dataAjuizamento
hits.hits[0]._source.dataHoraUltimaAtualizacao
hits.hits[0]._source.orgaoJulgador.codigo
hits.hits[0]._source.orgaoJulgador.nome
hits.hits[0]._source.assuntos[*].nome
hits.hits[0]._source.movimentos[*]
```

