# --- Build Stage ---
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY src/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt


# --- Runtime Stage ---
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies for postgres
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local
COPY src/ .

# Create non-root user and data directory
RUN useradd -m appuser && \
    mkdir -p /app/data && \
    chown -R appuser:appuser /app
USER appuser

# Set environment variables
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
