# projetos6 — JurisTCU API

REST API built with Django + Django REST Framework exposing the [LeandroRibeiro/JurisTCU](https://huggingface.co/datasets/LeandroRibeiro/JurisTCU) dataset.

---

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (package manager)

---

## Project structure

```
projetos6/
├── api/                        # Django project
│   ├── api/                    # Settings, URLs, WSGI
│   │   ├── settings.py
│   │   └── urls.py
│   ├── core/                   # Main app
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── load_juristcu.py  # Custom management command
│   │   ├── models.py
│   │   ├── serializers.py
│   │   └── views.py
│   ├── juristcu.db             # SQLite database (created after loading)
│   └── manage.py
├── pyproject.toml
└── README.md
```

---

## Setup

### 1. Create and activate the virtual environment

```bash
uv venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Apply Django migrations

This creates the internal Django tables (auth, sessions, etc.) without touching the dataset tables.

```bash
cd api
python manage.py migrate
```

### 4. Load the dataset into SQLite

Downloads the dataset from HuggingFace and populates the `docs`, `qrels`, and `queries` tables.

```bash
python manage.py load_juristcu
```

Optional flags:

| Flag | Default | Description |
|---|---|---|
| `--repo` | `LeandroRibeiro/JurisTCU` | HuggingFace dataset repo |
| `--db` | settings `DATABASE` path | Override SQLite file path |
| `--if-exists` | `replace` | `replace` / `append` / `fail` |

Example with custom path:

```bash
python manage.py load_juristcu --db /tmp/custom.db --if-exists append
```

### 5. Run the development server

```bash
python manage.py runserver
```

---

## API endpoints

Base URL: `http://localhost:8000/api/`

| Method | URL | Description |
|---|---|---|
| `GET` | `/api/documents/` | List all documents (paginated) |
| `GET` | `/api/documents/{key}/` | Get a single document |

### Filtering

Append any of these as query parameters:

```
/api/documents/?area=Licitações
/api/documents/?ano_acordao=2023
/api/documents/?colegiado=Plenário&tipo_processo=TC
/api/documents/?paradigmatico=S
```

Available filter fields: `key`, `num_acordao`, `ano_acordao`, `colegiado`, `area`, `tema`, `subtema`, `tipo_processo`, `tipo_recurso`, `autor_tese`, `paradigmatico`.
