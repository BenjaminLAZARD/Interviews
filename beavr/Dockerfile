# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV POETRY_VERSION=1.8
# makes poetry available after pipx installation
ENV PATH="$PATH:/root/.local/bin"

# Install pipx and Poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl python3 python3-pip \
    && pip install --upgrade pip \
    && pip install pipx \
    && pipx ensurepath \
    && pipx install poetry \
    && apt-get remove --purge -y curl \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
# Set the working directory in the container
WORKDIR /beavr_app

# Copy the pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock* /beavr_app/

# Install dependencies
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

# Copy the rest of the application code
COPY . /beavr_app

# Expose port 8000 and define the default command to run the FastAPI application
EXPOSE 8000
CMD ["uvicorn", "beavr_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
