# HR SQLcoder

[![CI](https://github.com/enavid/hr-sqlcoder/actions/workflows/ci.yml/badge.svg)](https://github.com/enavid/hr-sqlcoder/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.35+-ff4b4b.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A Streamlit app that turns natural-language HR questions into PostgreSQL queries using a locally hosted Ollama model — with a built-in Prompt Studio for prompt engineering.

---

## Stack

- **LLM** — Ollama (`llama3-sqlcoder`) running on a local GPU server
- **UI** — Streamlit multi-page app
- **DB** — PostgreSQL (`hr_mvp` schema)
- **Container** — Docker + GitHub Container Registry
- **Reverse proxy** — Nginx with SSL + Basic Auth

---

## Local development

```bash
git clone git@github.com:enavid/hr-sqlcoder.git
cd hr-sqlcoder
cp .env.example .env        # fill in your values
pip install -r requirements.txt
streamlit run app.py
```

---

## Production deployment

See **[Deploy on Ubuntu 24](#deploy-on-ubuntu-24)** section below.

---

## Pages

| Page                    | Description                                             |
| ----------------------- | ------------------------------------------------------- |
| **Chat**          | Ask questions in Persian or English, get SQL, run on DB |
| **Prompt Studio** | Create and manage named prompt templates                |

---

## Environment Variables

| Variable                                | Description                            |
| --------------------------------------- | -------------------------------------- |
| `OLLAMA_URL`                          | Ollama generate endpoint               |
| `OLLAMA_TAGS_URL`                     | Ollama tags endpoint (health check)    |
| `MODEL_NAME`                          | Model name in Ollama                   |
| `SCHEMA_PATH`                         | Path to `schema_context.txt`         |
| `DB_HOST` / `DB_PORT` / `DB_NAME` | PostgreSQL connection                  |
| `DB_USER` / `DB_PASSWORD`           | PostgreSQL credentials                 |
| `MODEL_TEMPERATURE`                   | Sampling temperature (default `0.4`) |
| `MODEL_TOP_P`                         | Top-p sampling (default `0.5`)       |

---

## Deploy on Ubuntu 24

### 1. Install Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER && newgrp docker
```

### 2. Clone the repo on the server

```bash
git clone https://github.com/enavid/hr-sqlcoder.git
cd hr-sqlcoder
```

### 3. Configure environment

```bash
cp .env.example .env
nano .env        # fill in all values
```

### 4. Add SSL certificates

```bash
sudo mkdir -p /etc/ssl/hr-sqlcoder
sudo cp fullchain.pem privkey.pem chain.pem cert.pem /etc/ssl/hr-sqlcoder/
sudo chmod 600 /etc/ssl/hr-sqlcoder/privkey.pem
```

### 5. Create Basic Auth password

```bash
mkdir -p nginx/auth
docker run --rm httpd:alpine htpasswd -nb YOUR_USERNAME YOUR_PASSWORD \
  > nginx/auth/.htpasswd
```

Replace `YOUR_USERNAME` and `YOUR_PASSWORD` with your credentials.

### 6. Add runtime data files

```bash
touch prompts.json
cp /path/to/your/schema_context.txt .
```

### 7. Pull and start

```bash
docker compose pull
docker compose up -d
```

### 8. Verify

```bash
docker compose ps
curl -k https://hr.aminraay.ir   # should return 401 (auth required)
```

---

## Update to latest version

```bash
docker compose pull
docker compose up -d
```
