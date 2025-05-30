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
# Default port for local runs; matches main.py configuration
ENV PORT=8000
# GCP Project ID for Secret Manager access
ENV GCP_PROJECT_ID=${GCP_PROJECT_ID}

# ---- Security: run as non-root user -----------------------------------------
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser /app
USER appuser


# ---- Start the service ------------------------------------------------------
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]