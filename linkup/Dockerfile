# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV POETRY_VERSION=1.8
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

# Set the working directory
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock* /app/

# Install the dependencies
RUN poetry install --no-root

# Copy the rest of your application code
COPY . /app

# Expose the port your app runs on
EXPOSE 8000

# Command to run your Uvicorn server
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
