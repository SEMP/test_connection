# Use Python slim image for smaller footprint
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for ping
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ping_checker.py .
COPY ping_daemon.py .
COPY analyze_logs.py .
COPY constants.py .

# Create data directory structure (will be mounted as volume)
RUN mkdir -p /app/data/config /app/data/logs /app/data/analysis

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash ping-user && \
    chown -R ping-user:ping-user /app

# Switch to non-root user
USER ping-user

# Expose any ports if needed (currently not used)
# EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Default command runs the daemon
CMD ["python", "ping_daemon.py"]