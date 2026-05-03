FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app content
COPY app/ .

# Security best practice: Run as non-root user
RUN useradd -m appuser
USER appuser

EXPOSE 5000

CMD ["python", "app.py"]
