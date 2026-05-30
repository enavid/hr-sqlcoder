
# HR SQLcoder

[![CI](https://github.com/enavid/hr-sqlcoder/actions/workflows/ci.yml/badge.svg)](https://github.com/enavid/hr-sqlcoder/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.35+-ff4b4b.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://claude.ai/chat/LICENSE)

A Streamlit app that turns natural-language HR questions into PostgreSQL queries using a locally hosted Ollama model — with a built-in Prompt Studio for prompt engineering.

---

## Stack

* **LLM** — Ollama (`llama3-sqlcoder`) running on a local GPU server
* **UI** — Streamlit multi-page app
* **DB** — PostgreSQL (`hr_mvp` schema)
* **Container** — Docker + GitHub Container Registry

---

## Setup

### 1. Clone

```bash
git clone git@github.com:enavid/hr-sqlcoder.git
cd hr-sqlcoder
```

### 2. Configure

```bash
cp .env.example .env
# fill in your values
```

### 3. Add schema

Paste your HR schema into `schema_context.txt`.

### 4. Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

### 5. Run with Docker

```bash
docker pull ghcr.io/enavid/hr-sqlcoder:latest
docker compose up -d
```

---

## Pages

| Page                    | Description                                             |
| ----------------------- | ------------------------------------------------------- |
| **Chat**          | Ask questions in Persian or English, get SQL, run on DB |
| **Prompt Studio** | Create and manage named prompt templates                |

---

## Environment Variables

| Variable                            | Description                            |
| ----------------------------------- | -------------------------------------- |
| `OLLAMA_URL`                      | Ollama generate endpoint               |
| `OLLAMA_TAGS_URL`                 | Ollama tags endpoint (health check)    |
| `MODEL_NAME`                      | Model name in Ollama                   |
| `SCHEMA_PATH`                     | Path to `schema_context.txt`         |
| `DB_HOST`/`DB_PORT`/`DB_NAME` | PostgreSQL connection                  |
| `DB_USER`/`DB_PASSWORD`         | PostgreSQL credentials                 |
| `MODEL_TEMPERATURE`               | Sampling temperature (default `0.4`) |
| `MODEL_TOP_P`                     | Top-p sampling (default `0.5`)       |
