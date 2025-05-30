# ---- Base image -------------------------------------------------------------
FROM python:3.10-slim

# ---- Install system dependencies for Google Cloud SDK ----------------------
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# ---- Install Google Cloud SDK -----------------------------------------------
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - \
    && apt-get update && apt-get install -y google-cloud-cli \
    && rm -rf /var/lib/apt/lists/*

# ---- Install Python dependencies first (cache layer) ------------------------
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copy application code --------------------------------------------------
COPY . .

# ---- Make start script executable -------------------------------------------
RUN chmod +x start.sh

# ---- Runtime configuration --------------------------------------------------
# Flush stdout/stderr immediately
ENV PYTHONUNBUFFERED=1
# Make app modules importable
ENV PYTHONPATH=/app
# Default port for local runs; matches main.py configuration
ENV PORT=8000

# ---- Security: run as non-root user -----------------------------------------
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser /app
USER appuser

# ---- Start the service ------------------------------------------------------
CMD ["sh", "-c", "./start.sh"]