Essa estratégia de **Ingestão em Lote (Bulk)** com o padrão **Adapter** é ideal para garantir a escalabilidade do dataset e a manutenibilidade do código, permitindo que o sistema suporte o **DataJud** agora e outras fontes (como diários oficiais ou APIs de tribunais específicos) no futuro.

Aqui está a estruturação da **Engenharia Reversa** focada nesse fluxo lógico:

### 3. Engenharia Reversa e Lógica de Programação (O "Como")

#### **A. Input de Dados e Fontes**

* 
**Como o dado entra:** O dado entra no sistema através de requisições **HTTP GET/POST** para o endpoint `_search` do DataJud. O sistema utiliza um parâmetro dinâmico de `size` (ex: 50) para extrair o volume máximo de *matches* permitido por requisição, otimizando a coleta de processos do **TRT6**.


* **Fontes Externas:** A funcionalidade depende da **API Pública do CNJ (DataJud)**. O sistema implementa o padrão **Adapter** para traduzir o JSON nativo da API (como os campos `assuntos` e `movimentos`) em uma interface única e padronizada para o dataset interno.



#### **B. Processamento e Lógica de Negócio (Backend)**

* 
**Gatilhos (Triggers):** O fluxo é disparado por um job de sincronização que envia a lista de tópicos e recebe o lote de dados da API.


* **Algoritmos:**
* 
**Deduplicação:** Um método recebe a lista de objetos do Adapter e realiza uma operação de conjunto (*set difference*) comparando o `numeroProcesso` recebido com os registros existentes no banco de dados para filtrar apenas os novos itens.


* 
**Vetorização:** Após o filtro, os novos registros passam por modelos de **NLP** para gerar **embeddings** a partir das ementas antes da persistência.




* 
**Estrutura de Dados:** O sistema utiliza uma estrutura **híbrida**:


* 
**Relacional:** Onde é executado o **Bulk Create** para salvar os metadados (valores, datas e varas) de forma atômica e performática.


* 
**Vetorial:** Onde são armazenados os vetores correspondentes para habilitar a busca por similaridade.





#### **C. Performance e Feedback (Frontend)**

* 
**Estados da Interface:** A aplicação, sendo uma **SPA**, utiliza **esqueletos de carregamento (skeletons)** para indicar o progresso do processamento em lote e da verificação de duplicidade no backend.


* 
**Atualização em Tempo Real:** O frontend utiliza chamadas **HTTP assíncronas** para atualizar os contadores do dataset e os dashboards de jurimetria assim que o **Bulk Create** é confirmado pelo servidor, garantindo que o usuário visualize o crescimento da base de dados sem recarregar a página.



---

**Mapeamento de Fluxo do Backend:**

1. **Request:** Busca 50 registros por tópico no DataJud.
2. **Adapter:** Normaliza o JSON para a interface `ProcessoTrabalhista`.
3. **Filter:** `get_non_existent(lista_api)` -> retorna apenas IDs inéditos no DB.
4. **Bulk Create:** Salva o lote de novos processos em uma única transação.

**Gostaria que eu ajudasse a definir a interface única do seu Adapter para garantir que campos como "Indenização por Dano Moral" sejam sempre mapeados da mesma forma, independente da API de origem?**
