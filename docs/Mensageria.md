Para criar uma arquitetura profissional que suporte o volume de dados e a instabilidade de scrapers e LLMs, vamos usar o padrão **Pipe and Filter** (Cano e Filtro) dentro de uma estrutura **Event-Driven**.

O segredo para "juntar os metadados" de forma limpa é o conceito de **Mensagem Enriquecida**: a mensagem que viaja pela fila começa apenas com o número do processo e, a cada etapa, um novo "pedaço" de informação é adicionado a ela.

---

## 🏗️ Arquitetura Detalhada: "The Process Pipeline"

### 1. Componentes do Ecossistema
* **Django API (The Brain):** Centraliza o banco de dados (PostgreSQL) e expõe endpoints para consulta do Frontend e atualização dos Workers.
* **Ingestor Job (The Trigger):** Script Python (pode ser um comando Django Admin) que roda periodicamente.
* **RabbitMQ (The Broker):** Gerencia as filas de tarefas.
* **Worker Scraper (The Crawler):** Especializado em navegar no TRT6 (Playwright/Selenium).
* **Worker LLM (The Analyst):** Especializado em extrair dados do PDF usando o LM Studio.
* **LocalStack/MinIO (The Vault):** Simula o S3 para guardar os PDFs.
* **Vue.js (The Dashboard):** Interface para monitorar o status de cada processo.

---

## 🔄 Fluxo de Comunicação: Quem fala com quem?

Abaixo, o passo a passo do ciclo de vida de um processo no seu sistema:

### Passo 1: Ingestão e Deduplicação
1.  O **Ingestor** faz um fetch na API externa do TRT6 e recebe uma lista de processos com **Metadados Iniciais** (ex: Vara, Data de Distribuição, Partes).
2.  O **Ingestor** faz uma chamada `HEAD` ou `GET` para a sua **API Django** para verificar se aquele `numero_processo` já existe.
3.  Se não existir, o Ingestor publica uma mensagem no **RabbitMQ** (Fila A) contendo: `{"numero": "...", "metadados_iniciais": {...}}`.

### Passo 2: O Scraping
1.  O **Worker Scraper** consome a mensagem da Fila A.
2.  Ele acessa o site do TRT6, resolve captchas e baixa o PDF.
3.  Ele faz o upload do PDF para o **LocalStack (S3)**.
4.  Ele "enriquece" a mensagem e a envia para a Fila B: 
    `{"numero": "...", "metadados_iniciais": {...}, "pdf_s3_path": "caminho/no/s3"}`.

### Passo 3: A Extração via LLM
1.  O **Worker LLM** consome a mensagem da Fila B.
2.  Ele baixa o PDF do **LocalStack** e extrai o texto.
3.  Ele envia o texto para o **LM Studio (API Local)** com um prompt pedindo um JSON estruturado.
4.  O Worker recebe o JSON da LLM (ex: valor da causa, pedidos, resumo).
5.  Agora ele tem tudo! Ele envia um `PATCH` final para a **API Django** com o objeto completo:
    ```json
    {
      "metadados_originais": "...", // O que veio do Ingestor
      "dados_extraidos_llm": "...",  // O que veio da LLM
      "status": "COMPLETO"
    }
    ```

### Passo 4: Visualização
1.  O **Frontend em Vue.js** faz polling ou usa WebSockets para mostrar ao usuário que o processo "X" mudou de status de `SCRAPING` para `FINALIZADO`.

---

## 🛠️ Detalhamento Técnico (A Integração Limpa)

| Componente | Comunicação | Responsabilidade |
| :--- | :--- | :--- |
| **Ingestor -> Django** | HTTP (REST) | Checagem de existência (Deduplicação). |
| **Ingestor -> RabbitMQ** | Protocolo AMQP | Publicar tarefa inicial com metadados. |
| **Scraper -> LocalStack** | Boto3 (SDK AWS) | Persistir o arquivo físico (.pdf). |
| **LLM Worker -> LM Studio** | HTTP (OpenAI Format) | Traduzir PDF em JSON estruturado. |
| **LLM Worker -> Django** | HTTP (PATCH/PUT) | Consolidar todos os dados no banco final. |
