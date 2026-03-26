# Integracao entre captcha_service e ingestion_service

## Objetivo

Definir uma interface de interacao clara entre os servicos de captcha e ingestao, com foco em:

- Separacao de responsabilidades
- Evolucao sem quebrar consumidores
- Facilidade de teste e observabilidade
- Aderencia aos principios SOLID (SRP, OCP e DIP)

## Contexto atual

- captcha_service ja resolve captcha, obtem tokenCaptcha e baixa integra (PDF/JSON/HTML) usando o fluxo do PJe TRT-6.
- ingestion_service esta mais exploratorio (notebook), com modelagem e normalizacao de dados DataJud.
- Existe necessidade de integrar o fluxo ponta a ponta: processo -> captcha -> documento integra -> extracao -> normalizacao -> persistencia.

## Principios de projeto aplicados

### SRP (Single Responsibility Principle)

Cada modulo deve ter uma unica responsabilidade de negocio:

- captcha_service:
  - Resolver captcha
  - Obter sessao (processo_id, token_desafio, token_captcha)
  - Baixar documento integra bruto
- ingestion_service:
  - Ler documento bruto
  - Extrair campos (PDF/DataJud)
  - Normalizar schema
  - Persistir e indexar
- orchestrator (novo modulo):
  - Coordenar fluxo entre os dois servicos
  - Gerenciar retry, timeout, idempotencia e correlacao

Evitar que captcha_service conheca regras de persistencia e evitar que ingestion_service conheca detalhes de automacao Playwright.

### OCP (Open/Closed Principle)

O design deve permitir extensao sem editar o nucleo:

- Novas fontes de documento (outros tribunais, diario oficial, API externa) entram por adaptadores.
- Novas estrategias de extracao (regex, NLP, LLM, OCR alternativo) entram como plugins.
- Novos destinos de persistencia (PostgreSQL, S3, fila, data lake) entram por porta de saida.

### DIP (Dependency Inversion Principle)

Dependencias devem apontar para abstracoes (portas), nao para implementacoes concretas.

Portas sugeridas:

- CaptchaResolverPort
- DocumentoFetcherPort
- DocumentoParserPort
- ProcessoRepositoryPort
- EventPublisherPort

Implementacoes concretas (adapters) ficam substituiveis:

- PjePipelineAdapter
- PdfParserAdapter
- DjangoRepositoryAdapter
- JsonFileRepositoryAdapter
- QueuePublisherAdapter

## Arquitetura recomendada

### Camadas

1. Domain
- Entidades e contratos de negocio

2. Application
- Casos de uso (orquestracao)

3. Infrastructure
- Implementacoes externas (Playwright, HTTP, DB, fila, filesystem)

4. Interface
- CLI, API REST, scheduler, worker

### Fluxo de alto nivel

1. Recebe numeroProcesso + grau
2. Resolve captcha e obtem token
3. Baixa integra (pdf/json/html)
4. Salva artefato bruto com hash
5. Extrai campos de interesse
6. Normaliza para schema de ingestao
7. Persiste no destino
8. Publica evento de sucesso/falha

## Contrato de dados entre servicos

Sugestao: usar DTO unico de fronteira para nao acoplar o ingestion_service ao tipo interno do captcha_service.

Exemplo de contrato (captcha -> ingestion):

```json
{
  "correlationId": "uuid",
  "numeroProcesso": "00002564820255060171",
  "grau": "1",
  "processoId": "123456",
  "tokenCaptcha": "...",
  "documento": {
    "path": "captcha_service/documents/00002564820255060171_integra_http.pdf",
    "contentType": "application/pdf",
    "sha256": "...",
    "capturadoEm": "2026-03-18T12:34:56Z"
  },
  "metadata": {
    "fonte": "pje_trt6",
    "tentativa": 1
  }
}
```

Regra importante:

- ingestion_service nao deve depender de tokenCaptcha.
- ingestion_service deve depender apenas de documento bruto + metadados de rastreabilidade.

## Opcoes de integracao

### Opcao A: Integracao in-process (modular monolith)

Como funciona:

- Um use case unico importa adaptadores dos dois servicos e executa em memoria.

Vantagens:

- Menor complexidade operacional
- Mais rapido para entregar MVP
- Facil de debugar

Riscos:

- Acoplamento de deploy
- Escalabilidade independente limitada

Quando usar:

- Fase inicial do projeto

### Opcao B: Integracao por REST interno

Como funciona:

- captcha_service expoe endpoint para resolver e entregar artefato
- ingestion_service consome endpoint e processa

Vantagens:

- Separacao de deploy
- Contrato explicito e versionavel

Riscos:

- Mais latencia
- Necessita controle de resiliencia de rede

Quando usar:

- Equipes separadas ou necessidade de escalar individualmente

### Opcao C: Integracao orientada a eventos (fila)

Como funciona:

- captcha_service publica evento DocumentoCapturado
- ingestion_service consome evento e processa assincronamente

Vantagens:

- Alto desacoplamento
- Boa resiliencia
- Escalabilidade horizontal

Riscos:

- Maior complexidade de operacao
- Exige idempotencia forte

Quando usar:

- Volume alto e picos de processamento

## Recomendacao pratica (estrategia em 3 fases)

1. Fase 1 (agora): Opcao A
- Criar orquestrador local e portas
- Padronizar DTO de fronteira
- Persistir artefatos e logs com correlationId

2. Fase 2: Opcao B
- Expor endpoints internos
- Versionar contrato (v1)
- Implementar retries com backoff e circuit breaker

3. Fase 3: Opcao C
- Introduzir broker (RabbitMQ, Redis Streams ou SQS)
- Implementar DLQ, reprocessamento e metricas de lag

## Interface de codigo (sugestao)

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass
class DocumentoBruto:
    numero_processo: str
    grau: str
    path: str
    content_type: str
    sha256: str
    correlation_id: str


class CaptchaResolverPort(Protocol):
    def resolver(self, numero_processo: str, grau: str) -> dict: ...


class DocumentoFetcherPort(Protocol):
    def baixar_integra(self, sessao: dict) -> DocumentoBruto: ...


class DocumentoParserPort(Protocol):
    def extrair(self, documento: DocumentoBruto) -> dict: ...


class ProcessoRepositoryPort(Protocol):
    def salvar(self, processo_normalizado: dict) -> None: ...
```

Exemplo de caso de uso:

```python
class IngerirProcessoUseCase:
    def __init__(self, resolver, fetcher, parser, repo):
        self.resolver = resolver
        self.fetcher = fetcher
        self.parser = parser
        self.repo = repo

    def executar(self, numero_processo: str, grau: str) -> dict:
        sessao = self.resolver.resolver(numero_processo, grau)
        documento = self.fetcher.baixar_integra(sessao)
        processo = self.parser.extrair(documento)
        self.repo.salvar(processo)
        return processo
```

## Boas praticas operacionais

### Idempotencia

- Chave idempotente sugerida: tribunal + grau + numeroProcesso + sha256(documento)
- Nao duplicar ingestao quando o mesmo documento chegar novamente

### Observabilidade

- CorrelationId em todos os logs
- Metricas:
  - tempo_resolucao_captcha
  - taxa_sucesso_captcha
  - tempo_download_documento
  - taxa_falha_parser
  - latencia_total_ingestao

### Resiliencia

- Timeout por etapa
- Retry com backoff exponencial
- Separar erros recuperaveis (rede, timeout) de nao recuperaveis (schema invalido)

### Seguranca

- Nunca logar tokenCaptcha completo
- Mascarar segredos e chaves de API

## Estrutura de pastas sugerida

```text
projetos6/
  integration/
    domain/
      contracts.py
      entities.py
    application/
      use_cases.py
    infrastructure/
      captcha_adapter.py
      parser_adapter.py
      repository_adapter.py
      event_adapter.py
    interface/
      cli.py
      api.py
```

## Testes recomendados

- Unitarios:
  - Use case com mocks das portas
  - Parser de PDF com fixtures reais
- Contrato:
  - Validar schema do DTO entre captcha e ingestao
- Integracao:
  - Fluxo completo em ambiente de homologacao TRT-6
- Regressao:
  - Conjunto de captchas e PDFs historicos

## Comandos sugeridos com uv

```bash
uv run python -m integration.interface.cli --numero 0000256-48.2025.5.06.0171 --grau 1
uv run python -m pytest
```

## Conclusao

A melhor estrategia e iniciar com integracao in-process e design por portas (DIP), mantendo responsabilidade clara por modulo (SRP) e extensibilidade por adaptadores (OCP). Isso entrega valor rapido sem sacrificar evolucao para REST ou fila no futuro.