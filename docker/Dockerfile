# --- Stage 1: The Builder ---
FROM python:3.12-slim AS builder

# 1. Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 2. Set working directory
WORKDIR /app

# 3. Enable bytecode compilation for faster startups
ENV UV_COMPILE_BYTECODE=1

# 4. Copy ONLY dependency files first (for layer caching)
COPY pyproject.toml uv.lock ./

# 5. Install dependencies without the project itself
RUN uv sync --frozen --no-install-project --no-dev

# --- Stage 2: The Runtime ---
FROM python:3.12-slim

WORKDIR /app

# 6. Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# 7. Copy the actual source code
COPY app/ ./app/

# 8. Set the Path to use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# 9. Execution command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
