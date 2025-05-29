# ---- Base image -------------------------------------------------------------
FROM python:3.10-slim

# ---- Install Python dependencies first (cache layer) ------------------------
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copy application code --------------------------------------------------
COPY . .

# ---- Runtime configuration --------------------------------------------------
# Flush stdout/stderr immediately
ENV PYTHONUNBUFFERED=1
# Make app modules importable
ENV PYTHONPATH=/app
# Default port for local runs; Cloud Run will override with its own $PORT
ENV PORT=8080

# ---- Security: run as non-root user -----------------------------------------
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser /app
USER appuser

ENV OPENAI_API_KEY="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"
# ---- Start the service ------------------------------------------------------
# Cloud Run injects $PORT; fall back to 8080 when run locally
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]