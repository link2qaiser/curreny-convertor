FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing bytecode files
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev curl && rm -rf /var/lib/apt/lists/*

# Install Poetry temporarily to generate requirements files
RUN pip install poetry poetry-plugin-export

# Configure Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock ./

# Set default ENV_STATE if not provided
ARG ENV_STATE=prod
ENV ENV_STATE=${ENV_STATE}

# Generate requirements files and install dependencies based on environment
RUN if [ "$ENV_STATE" = "dev" ] ; then \
        echo "🔧 Generating requirements files for DEVELOPMENT" && \
        poetry export -f requirements.txt --output requirements.txt --without-hashes && \
        poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes && \
        echo "📦 Installing ALL dependencies (dev + prod)" && \
        pip install --no-cache-dir -r requirements-dev.txt ; \
    else \
        echo "🚀 Generating requirements file for PRODUCTION" && \
        poetry export -f requirements.txt --output requirements.txt --without-hashes && \
        echo "📦 Installing PRODUCTION dependencies only" && \
        pip install --no-cache-dir -r requirements.txt ; \
    fi

# Remove Poetry after generating requirements (not needed at runtime)
RUN pip uninstall -y poetry && \
    rm -rf $POETRY_CACHE_DIR /root/.cache/pip

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application directly with uvicorn (no Poetry needed)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]