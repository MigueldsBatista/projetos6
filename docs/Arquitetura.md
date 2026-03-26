Usar o **`uv`** é uma excelente escolha. Ele é atualmente a ferramenta mais rápida e moderna do ecossistema Python. Para um monorepo de microsserviços, a melhor forma de gerenciar isso é através de **UV Workspaces**.

Essa abordagem permite que você tenha dependências compartilhadas e um ambiente de desenvolvimento unificado, mas mantenha a liberdade de buildar cada serviço de forma independente.

---

## 🏗️ Arquitetura do Monorepo

Sugiro a estrutura abaixo. Ela separa a lógica de negócio (serviços) da lógica compartilhada (modelos de dados, schemas e clientes de infra).

```text
projeto-trt6/
├── pyproject.toml           # Configuração do Workspace (Raiz)
├── uv.lock                  # Lockfile único para todo o projeto
├── shared/                  # Código compartilhado (Lib interna)
│   ├── pyproject.toml
│   └── src/
│       └── shared/
│           ├── schemas.py   # Pydantic models da mensagem
│           ├── s3_client.py # Wrapper do Boto3 para o LocalStack
│           └── database.py  # Conexão base se não for via Django
├── apps/
│   ├── api-django/          # O Core / Dashboard
│   │   ├── pyproject.toml
│   │   └── ...
│   ├── worker-scraper/      # Worker de Scraping (Playwright/Selenium)
│   │   ├── pyproject.toml
│   │   └── ...
│   ├── worker-llm/          # Worker de IA (Integração LM Studio)
│   │   ├── pyproject.toml
│   │   └── ...
│   └── ingestor/            # Script de Ingestão (Job)
│       ├── pyproject.toml
│       └── ...
└── docker-compose.yml
```

---

## 📄 Gerenciando os `pyproject.toml`

Com o `uv`, você terá um arquivo na raiz que "enxerga" todos os outros.

### 1. No Root (`/pyproject.toml`)
Aqui você define que o projeto é um workspace.

```toml
[project]
name = "projeto-trt6-monorepo"
version = "0.1.0"
dependencies = [] # Dependências globais se houver (ex: ruff, pytest)

[tool.uv.workspace]
members = ["apps/*", "shared"]
```

### 2. No Shared (`/shared/pyproject.toml`)
Este módulo contém o que todos usam (ex: Pydantic para validar o JSON da LLM).

```toml
[project]
name = "shared"
version = "0.1.0"
dependencies = [
    "pydantic>=2.0",
    "boto3>=1.28", # Para o S3/Localstack
]
```

### 3. Nos Workers (ex: `/apps/worker-llm/pyproject.toml`)
Aqui você declara a dependência do módulo `shared`. O `uv` fará o link simbólico automaticamente.

```toml
[project]
name = "worker-llm"
version = "0.1.0"
dependencies = [
    "shared",       # Referência ao seu pacote interno
    "requests",     # Para falar com o LM Studio
    "celery",
]

[tool.uv.sources]
shared = { workspace = true } # Indica que deve buscar no monorepo
```

---

## 🔄 Como os módulos se conversam?

Para manter a integração "limpa" (como você pediu), o segredo é o módulo **`shared`**.

1.  **Schemas de Mensagem:** Defina uma classe Pydantic em `shared/schemas.py`.
    ```python
    class ProcessoTask(BaseModel):
        numero: str
        metadados_iniciais: dict
        pdf_path: Optional[str] = None
        dados_llm: Optional[dict] = None
    ```
2.  **Importação:** Tanto o `ingestor` quanto o `worker-scraper` e o `worker-llm` importarão esse mesmo schema: `from shared.schemas import ProcessoTask`.
3.  **Vantagem:** Se você mudar o nome de um campo, todos os microsserviços "quebram" no desenvolvimento, garantindo que você não envie mensagens com formatos errados na fila.

---

## 🚀 Comandos Úteis com UV

* **Sincronizar tudo:** `uv sync` (Cria um `.venv` na raiz que contém todos os pacotes de todos os apps).
* **Adicionar dependência num app específico:** `uv add --package worker-scraper playwright`.
* **Rodar um comando:** `uv run --package api-django python manage.py runserver`.

## 📦 Estratégia de Docker (Para Produção/Vagas)

Nas vagas, eles olham muito o tamanho da imagem. Como você usa `uv`, pode fazer builds multi-stage muito eficientes:

1.  Use a imagem `ghcr.io/astral-sh/uv:debian` para compilar.
2.  Gere um **Compiled Virtualenv**.
3.  Copie apenas o venv para uma imagem `python:slim`.

Isso mostra que você sabe otimizar o pipeline de CI/CD.



**Essa estrutura de Workspaces faz sentido para você ou prefere algo mais simples com um único ambiente para tudo?**