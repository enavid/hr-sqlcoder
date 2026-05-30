# =============================================================================
# Stage 1 — builder
# Install all dependencies into an isolated prefix so we copy only what's
# needed into the final image (no pip cache, no build tools).
# =============================================================================
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

# System deps required to compile psycopg2-binary (libpq headers)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# =============================================================================
# Stage 2 — runtime
# Minimal image: only the app code + installed packages from the builder.
# Runs as a non-root user for security.
# =============================================================================
FROM python:3.12-slim-bookworm AS runtime

# Runtime-only system lib for psycopg2
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN groupadd --gid 1001 appgroup \
    && useradd --uid 1001 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source (respects .dockerignore)
COPY --chown=appuser:appgroup . .

# Streamlit config is baked in; secrets come from --env-file at runtime
# Never copy .env into the image

USER appuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')"

ENTRYPOINT ["streamlit", "run", "app.py", \
    "--server.port=8501", \
    "--server.address=0.0.0.0", \
    "--server.headless=true", \
    "--server.enableCORS=false", \
    "--server.enableXsrfProtection=true"]
