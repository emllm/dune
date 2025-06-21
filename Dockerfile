FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.7.1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

# Configure Poetry
RUN poetry config virtualenvs.create false

# Copy project files
COPY pyproject.toml poetry.lock* ./


# Copy application code
COPY . .

# Install the package with all dependencies
RUN poetry install --no-interaction --no-ansi --no-root
RUN poetry install --no-interaction --no-ansi

# Create output directory
RUN mkdir -p /app/output

# Set the default command
CMD ["poetry", "run", "python", "dune.py"]