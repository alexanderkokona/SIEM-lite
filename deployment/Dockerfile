FROM python:3.11-slim

LABEL maintainer="SIEM-lite Contributors"
LABEL description="SIEM-lite: Auth log security pipeline"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY requirements.txt setup.py README.md ./
COPY config/ ./config/
COPY event/ ./event/
COPY scripts/ ./scripts/
COPY deployment/ ./deployment/

# Create non-root user
RUN useradd -m -u 1000 siem-lite && \
    mkdir -p /app/data/raw /app/data/processed /app/logs && \
    chown -R siem-lite:siem-lite /app

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Install the application
RUN pip install --no-cache-dir -e .

# Switch to non-root user
USER siem-lite

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import event; print('OK')" || exit 1

# Run the verification script as entry point
ENTRYPOINT ["python3", "-m", "scripts.verify_auth_log_access"]
