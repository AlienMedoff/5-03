# 🐳 Multi-stage Dockerfile for Aether Multi-Agent Bot
FROM python:3.11-slim as base

# 🏗️ Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 📁 Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 📦 Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 🏃‍♂️ Create non-root user
RUN useradd --create-home --shell /bin/bash aether

# 📁 Set working directory
WORKDIR /app

# 📋 Copy application code
COPY --chown=aether:aether . .

# 🔐 Create necessary directories
RUN mkdir -p /app/logs /app/data /app/uploads && \
    chown -R aether:aether /app

# 🚀 Production stage
FROM base as production

# 🏃‍♂️ Switch to non-root user
USER aether

# 🚀 Expose port
EXPOSE 8080

# 🏥 Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 🚀 Start command
CMD ["uvicorn", "bot.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]

# 🧪 Development stage
FROM base as development

# 🏃‍♂️ Switch to non-root user
USER aether

# 🚀 Development start command
CMD ["uvicorn", "bot.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

# 🧪 Testing stage
FROM base as testing

# 🧪 Install test dependencies
RUN pip install pytest pytest-asyncio pytest-cov

# 📋 Copy test files
COPY --chown=aether:aether tests/ ./tests/

# 🧪 Test command
CMD ["pytest", "tests/", "-v", "--cov=.", "--cov-report=html"]
