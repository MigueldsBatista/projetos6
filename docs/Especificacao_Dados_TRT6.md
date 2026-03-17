# Especificacao de dados TRT6 (JSON DataJud + PDF integra)

## 1) Objetivo
Definir um esquema de dados enxuto para ingestao de processos trabalhistas, combinando:
- JSON do DataJud (metadados e historico)
- PDF de integra (conteudo decisorio, valores e obrigacoes)

A meta e reduzir o payload bruto e manter apenas campos com utilidade para:
- busca e filtros
- analise de resultados
- indicadores financeiros e de desfecho

## 2) Colunas recomendadas (MVP)

### 2.1 Identificacao do processo
- processo_numero_cnj (string, PK logica)
- processo_id_datajud (string)
- tribunal (string)
- grau (string)
- classe_codigo (int)
- classe_nome (string)
- orgao_julgador_codigo (string)
- orgao_julgador_nome (string)

### 2.2 Datas relevantes
- data_ajuizamento (date)
- data_ultima_atualizacao_datajud (datetime)
- data_ato_principal_pdf (date, nullable)
- data_sentenca_pdf (date, nullable)
- data_arquivamento_pdf (date, nullable)

### 2.3 Partes e assunto (enxuto)
- reclamante_nome (string, nullable)
- reclamado_nome (string, nullable)
- assuntos (json array de strings)

### 2.4 Resultado processual e financeiro
- tipo_ato_principal (enum: despacho, acordo_homologado, sentenca, acordao, outro)
- decisao_resumo (text curto)
- status_processo (enum: em_andamento, acordo_homologado, sentenciado, arquivado)
- desfecho (enum: acordo_favoravel, sentenca_procedente, sentenca_parcialmente_procedente, sentenca_improcedente, sentenca_extinta, recurso_provido, recurso_desprovido, em_andamento, arquivado_sem_decisao)
- resultado_reclamante (enum: ganhou, ganhou_parcial, perdeu, sem_decisao)
- palavras_chave_desfecho (json array de strings encontradas que levaram a classificacao)
- valor_causa (decimal(14,2), nullable)
- valor_acordo_total (decimal(14,2), nullable)
- valor_pago_reclamante (decimal(14,2), nullable)
- valor_pago_advogado (decimal(14,2), nullable)
- custas_valor (decimal(14,2), nullable)
- custas_percentual (decimal(5,2), nullable)
- multa_inadimplencia_percentual (decimal(5,2), nullable)
- prazo_pagamento_texto (string, nullable)

### 2.5 Auditoria e rastreabilidade
- fonte_json_capturado_em (datetime)
- fonte_pdf_capturado_em (datetime)
- pdf_numero_paginas (int)
- parser_versao (string)
- confianca_extracao (decimal(5,2), nullable)
- raw_source_json (json)
- raw_pdf_texto (text)

## 3) O que NAO precisa guardar no dataset principal
Campos do DataJud que podem ficar apenas no bruto (raw_source_json):
- _index, _id, _score
- movimentos completos sem agregacao
- complementosTabelados completos
- estruturas duplicadas de publicacao/disponibilizacao

Manter no principal somente agregados uteis de movimentos, por exemplo:
- ultimo_movimento_nome
- ultimo_movimento_data
- quantidade_movimentos

## 4) O que extrair do PDF (alem de decisao e taxa)
Recomendado extrair tambem:
- tipo do ato (despacho, acordo homologado, sentenca)
- resumo da decisao em 1-3 frases
- valor da causa
- valor do acordo
- valores por beneficiario (reclamante, advogado)
- custas (valor e percentual)
- multa por inadimplencia (percentual)
- condicao de quitacao (geral/plena/parcial)
- obrigacoes com prazo (ex: data limite de pagamento)
- sinal de encerramento/arquivamento

### 4.1 Padroes de desfecho para classificacao de sucesso

Objetivo: classificar cada processo em "desfecho" e "resultado_reclamante" para calcular taxa de sucesso.

**Desfecho: acordo_favoravel** (resultado_reclamante: ganhou)
- Palavras-chave: "ACORDO HOMOLOGADO", "CONCILIACAO"
- Condicoes: DEVE haver valor pagavel ao reclamante (regex: "pagara.* ao reclamante .* R\$")
- Exemplo: processo 0000256-48.2025.5.06.0171 (R$ 2.500 ao reclamante)

**Desfecho: sentenca_procedente** (resultado_reclamante: ganhou)
- Palavras-chave no bloco SENTENCA: "procedente", "condenado", "condenamos", "procedencia"
- Contexto: frase apos SENTENCA com esses termos
- Exemplo: "Pelo exposto, JULGO PROCEDENTE a reclamaçao..."

**Desfecho: sentenca_parcialmente_procedente** (resultado_reclamante: ganhou_parcial)
- Palavras-chave: "parcialmente procedente", "em parte procedente"
- Contexto: SENTENCA com deferimento parcial
- Importante: capturar qual pedido foi deferido e qual foi indeferido

**Desfecho: sentenca_improcedente** (resultado_reclamante: perdeu)
- Palavras-chave: "improcedente", "rejeitada", "improvida", "negada"
- Contexto: bloco SENTENCA ou ACORDAO
- Exemplo: "Pelo exposto, JULGO IMPROCEDENTE a reclamaçao..."

**Desfecho: sentenca_extinta** (resultado_reclamante: sem_decisao)
- Palavras-chave: "extinto", "extinção", "sem resolução de mérito"
- Motivos tipicos: falta de acompanhamento, desistencia, inatividade
- Exemplo: "extinto sem resolução de mérito por falta de acompanhamento"

**Desfecho: recurso_provido** (resultado_reclamante: ganhou ou ganhou_parcial)
- Palavras-chave em bloco ACORDAO: "provido", "reformado"
- Contexto: quando há recurso que reverteu o desfecho anterior
- Importante: verificar qual era o resultado anterior

**Desfecho: recurso_desprovido** (resultado_reclamante: perdeu ou sem_decisao)
- Palavras-chave em ACORDAO: "desprovido", "mantida"
- Contexto: recurso que mantém a decisão anterior

**Desfecho: em_andamento** (resultado_reclamante: sem_decisao)
- Nao ha SENTENCA/ACORDAO/ACORDO no PDF
- Condicao: ultimo ato e despacho ou ata de audiência sem conclusao

**Desfecho: arquivado_sem_decisao** (resultado_reclamante: sem_decisao)
- Palavras-chave: "arquivem-se" sem anteceder de "SENTENCA" ou "ACORDO"
- Exemplo: processo arquivado por desistencia ou inatividade

### 4.2 Exemplo de classificacao (caso 0000256-48.2025.5.06.0171)
- tipo_ato_principal: acordo_homologado
- desfecho: acordo_favoravel
- resultado_reclamante: ganhou
- palavras_chave_desfecho: ["ACORDO HOMOLOGADO", "CONCILIACAO", "pagara ao reclamante", "R$ 2.500,00"]

## 5) Requisitos tecnicos da solucao
- Extracao PDF com pypdf usando a venv de api.
- Parser hibrido:
  - regex para valores monetarios, percentuais e datas
  - regras por palavras-chave para tipo de ato e status
- Normalizacao:
  - moeda para decimal com ponto
  - datas para ISO 8601
  - enums padronizados para status e tipo de ato
- Validacao:
  - manter texto bruto do PDF para auditoria
  - score de confianca por campo extraido
  - fila de revisao manual quando campo critico vier nulo

## 6) Exemplo de dado final (sample)
{
  "processo_numero_cnj": "0000256-48.2025.5.06.0171",
  "processo_id_datajud": "TRT6_G1_00002564820255060171",
  "tribunal": "TRT6",
  "grau": "G1",
  "classe_nome": "Acao Trabalhista - Rito Sumarissimo",
  "orgao_julgador_nome": "1a Vara do Trabalho do Cabo",
  "data_ajuizamento": "2025-04-15",
  "tipo_ato_principal": "acordo_homologado",
  "decisao_resumo": "Acordo homologado com quitacao geral e previsao de multa por inadimplencia.",
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
  "multa_inadimplencia_percentual": 100.00,
  "prazo_pagamento_texto": "parcela unica ate 30.07.2025",
  "data_sentenca_pdf": "2026-01-16",
  "data_arquivamento_pdf": "2026-01-16",
  "pdf_numero_paginas": 12,
  "confianca_extracao": 0.93
}

## 7) Proposta de prioridade (implementacao)
1. Fechar schema do MVP (itens da secao 2).
2. Implementar extrator PDF e parser de campos financeiros.
3. Implementar sumarizacao de decisao e classificacao de status.
4. Persistir dados normalizados + bruto para auditoria.
5. Criar validadores e relatorio de campos faltantes.

## 8) Dicionario campo a campo: referencia, descricao e como obter

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
| valor_causa | Valor economico atribuido a causa no processo. | PDF | Linha "Valor da causa" | Regex monetaria apos marcador "Valor da causa:" e normalizar para decimal. |
| valor_acordo_total | Valor total pactuado no acordo homologado. | PDF | Bloco "CONCILIACAO"/"ACORDO HOMOLOGADO" | Capturar valor total do acordo quando expresso como importancia total. |
| valor_pago_reclamante | Valor financeiro destinado ao reclamante no acordo/decisao. | PDF | Bloco de pagamento ao reclamante | Regex em frase "pagara ao reclamante ... R$ X". |
| valor_pago_advogado | Valor financeiro destinado ao advogado do reclamante. | PDF | Bloco de pagamento ao advogado | Regex em frase "pagara ao advogado ... R$ X". |
| custas_valor | Valor absoluto das custas processuais. | PDF | Linha com "Custas ... R$" | Regex de valor monetario apos marcador "Custas". |
| custas_percentual | Percentual de custas aplicado no ato. | PDF | Linha com "Custas" e "%" | Regex de percentual no mesmo trecho das custas. |
| multa_inadimplencia_percentual | Percentual de multa por inadimplencia/mora. | PDF | Linha "Multa de X%" | Regex de percentual apos palavra "Multa". |
| prazo_pagamento_texto | Texto com condicao e prazo de pagamento definidos no ato. | PDF | Bloco de pagamento | Capturar texto curto com prazo (ex: "parcela unica ... dia DD.MM.AAAA"). |
| fonte_json_capturado_em | Timestamp de captura do JSON na ingestao. | Derivado | Metadado da ingestao | Timestamp do momento de coleta do JSON. |
| fonte_pdf_capturado_em | Timestamp de captura do PDF na ingestao. | Derivado | Metadado da ingestao | Timestamp do momento de download/extracao do PDF. |
| pdf_numero_paginas | Quantidade total de paginas do PDF analisado. | PDF | PdfReader.pages | len(reader.pages). |
| parser_versao | Versao do parser responsavel pela extracao. | Derivado | Config da aplicacao | Versao semantica do parser (ex: 1.0.0). |
| confianca_extracao | Score agregado de confianca da extracao. | Derivado | Resultado do parser | Score agregado por completude e confianca das regras por campo. |
| raw_source_json | Conteudo bruto do registro retornado pela API. | DataJud | Hit completo da API | Persistir JSON bruto da fonte. |
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

Referencias no JSON DataJud (estrutura):
- hits.hits[0]._source.numeroProcesso
- hits.hits[0]._source.id
- hits.hits[0]._source.tribunal
- hits.hits[0]._source.grau
- hits.hits[0]._source.classe.codigo
- hits.hits[0]._source.classe.nome
- hits.hits[0]._source.dataAjuizamento
- hits.hits[0]._source.dataHoraUltimaAtualizacao
- hits.hits[0]._source.orgaoJulgador.codigo
- hits.hits[0]._source.orgaoJulgador.nome
- hits.hits[0]._source.assuntos[*].nome
- hits.hits[0]._source.movimentos[*] (apoio para status e trilha temporal)

## 10) Como usar desfecho para calcular % de sucesso

Com os campos "desfecho" e "resultado_reclamante" preenchidos, você pode gerar analises:

### 10.1 Taxa de sucesso basica
```sql
SELECT 
  COUNT(*) as total_processos,
  SUM(CASE WHEN resultado_reclamante = 'ganhou' THEN 1 ELSE 0 END) as processos_ganhos,
  SUM(CASE WHEN resultado_reclamante = 'ganhou_parcial' THEN 1 ELSE 0 END) as processos_parcial,
  SUM(CASE WHEN resultado_reclamante = 'perdeu' THEN 1 ELSE 0 END) as processos_perdidos,
  ROUND(100.0 * SUM(CASE WHEN resultado_reclamante IN ('ganhou', 'ganhou_parcial') THEN 1 ELSE 0 END) / COUNT(*), 2) as taxa_procedencia_percent
FROM processos
WHERE data_arquivamento_pdf IS NOT NULL  -- Apenas processos finalizados
```

### 10.2 Taxa por assunto
```sql
SELECT 
  assuntos,
  COUNT(*) as total,
  ROUND(100.0 * SUM(CASE WHEN resultado_reclamante = 'ganhou' THEN 1 ELSE 0 END) / COUNT(*), 2) as taxa_ganho_percent
FROM processos
WHERE resultado_reclamante IN ('ganhou', 'perdeu')
GROUP BY assuntos
ORDER BY taxa_ganho_percent DESC
```

### 10.3 Taxa por órgão julgador (jurisprudencia)
```sql
SELECT 
  orgao_julgador_nome,
  COUNT(*) as total_casos,
  SUM(CASE WHEN resultado_reclamante = 'ganhou' THEN 1 ELSE 0 END) as casos_ganhos,
  ROUND(100.0 * SUM(CASE WHEN resultado_reclamante = 'ganhou' THEN 1 ELSE 0 END) / COUNT(*), 2) as taxa_sucesso_percent,
  ROUND(AVG(valor_pago_reclamante), 2) as valor_medio_pago
FROM processos
WHERE resultado_reclamante IN ('ganhou', 'perdeu')
GROUP BY orgao_julgador_nome
ORDER BY taxa_sucesso_percent DESC
```

### 10.4 Analise de desfecho tipo a tipo
```sql
SELECT 
  desfecho,
  resultado_reclamante,
  COUNT(*) as quantidade,
  ROUND(AVG(valor_pago_reclamante), 2) as valor_medio,
  ROUND(AVG(DATEDIFF(day, data_ajuizamento, data_arquivamento_pdf)), 0) as dias_medio
FROM processos
WHERE desfecho IS NOT NULL
GROUP BY desfecho, resultado_reclamante
ORDER BY quantidade DESC
```

### 10.5 Palavras-chave com maior taxa de sucesso
```sql
SELECT 
  palavra,
  COUNT(*) as processos_com_palavra,
  ROUND(100.0 * SUM(CASE WHEN resultado_reclamante = 'ganhou' THEN 1 ELSE 0 END) / COUNT(*), 2) as taxa_sucesso_percent
FROM processos, 
LATERAL UNNEST(palavras_chave_desfecho) AS palavra
WHERE resultado_reclamante IN ('ganhou', 'perdeu')
GROUP BY palavra
HAVING COUNT(*) >= 5  -- Apenas palavras-chave com pelo menos 5 ocorrências
ORDER BY taxa_sucesso_percent DESC
```

Essas queries ajudam a identificar padrões de sucesso por tema, juiz, desfecho e até palavras-chave encontradas.
