# HR SQLcoder

A Streamlit app that converts natural-language HR questions into PostgreSQL queries
using a locally hosted Ollama model.

## Project structure

```
hr-sqlcoder/
├── app.py                      Entry point
├── .env                        Environment variables (copy from .env.example)
├── requirements.txt
├── schema_context.txt          Your HR schema description
├── prompts.json                Auto-generated; stores named prompt templates
│
├── .streamlit/
│   └── config.toml             Theme configuration
│
├── pages/
│   ├── chat.py                 Chat interface
│   └── prompt_studio.py        Prompt engineering interface
│
└── core/
    ├── config.py               Typed settings loaded from .env
    ├── llm.py                  Ollama API client
    ├── prompt.py               Prompt builder + default template
    ├── database.py             PostgreSQL query runner
    └── storage.py              Prompt template persistence (prompts.json)
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env` and fill in your values:

```bash
cp .env .env.local   # optional — or edit .env directly
```

Key variables:

| Variable           | Description                                  |
|--------------------|----------------------------------------------|
| `OLLAMA_URL`       | Full URL to the Ollama generate endpoint     |
| `OLLAMA_TAGS_URL`  | URL to the Ollama tags endpoint (health)     |
| `MODEL_NAME`       | Model name as registered in Ollama           |
| `SCHEMA_PATH`      | Path to your `schema_context.txt`            |
| `DB_HOST`          | PostgreSQL host                              |
| `DB_PORT`          | PostgreSQL port (default 5432)               |
| `DB_NAME`          | Database name                                |
| `DB_USER`          | Database user                                |
| `DB_PASSWORD`      | Database password                            |
| `MODEL_TEMPERATURE`| Sampling temperature (default 0.4)           |
| `MODEL_TOP_P`      | Top-p sampling (default 0.5)                 |

### 3. Add your schema

Paste your HR schema description into `schema_context.txt`.

### 4. Run

```bash
streamlit run app.py
```

## Pages

### Chat
- Type a question in Persian or English.
- The active prompt template is used automatically (shown in the sidebar).
- After SQL is generated, click **Run on DB** to execute it or **Dismiss** to skip.

### Prompt Studio
- Create and name multiple prompt templates.
- Edit the template text — unsaved changes are marked with `*`.
- Click **Set active** to make a template the default for the Chat page.
- Use the **Preview** expander to render the prompt with a sample question.
