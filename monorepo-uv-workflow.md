# Guia prático: Gerenciamento de dependências em monorepo Python com uv

## Estrutura do repositório

- `pyproject.toml` (raiz): define o workspace e os subprojetos.
- `apps/` e `shared/`: cada subprojeto tem seu próprio `pyproject.toml`.

## Como funcionam as dependências

- **Cada subprojeto** declara suas próprias dependências em seu `pyproject.toml`.
- **Dependências locais** (entre subprojetos):
  - Certifique-se que cada `[project]` tem um `name` único.
  - No consumidor, adicione a dependência pelo nome do projeto local.

## Adicionando dependências

- **Para um subprojeto:**
  ```sh
  cd caminho/do/subprojeto
  uv pip install <pacote>
  ```
  Isso atualiza o `pyproject.toml` do subprojeto.

- **Para dependências locais:**
  - No `pyproject.toml` do consumidor, adicione:
    ```toml
    dependencies = [
      "shared"
    ]
    ```
    (desde que `shared` tenha `[project] name = "shared"`)

## Comandos principais

- **Instalar dependências de todos os subprojetos:**
  ```sh
  uv pip install .
  ```
  (na raiz do projeto)

- **Instalar dependências de um subprojeto:**
  ```sh
  cd caminho/do/subprojeto
  uv pip install .
  ```

- **Adicionar nova dependência:**
  ```sh
  cd caminho/do/subprojeto
  uv pip install <pacote>
  ```

- **Atualizar dependências:**
  ```sh
  uv pip update
  ```

## Boas práticas

- Não coloque dependências de código no `pyproject.toml` da raiz.
- Sempre use o diretório do subprojeto para instalar/adicionar dependências.
- Mantenha o nome dos projetos únicos em `[project]`.
- Use o workspace do uv para facilitar o desenvolvimento integrado.

---

Dúvidas? Consulte este guia ou a documentação oficial do [uv](https://github.com/astral-sh/uv).
