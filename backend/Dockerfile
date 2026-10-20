FROM python:3.12-slim AS test
WORKDIR /app
COPY pyproject.toml ./
COPY src/ ./src/
COPY tests/ ./tests/
RUN pip install -e .[test]
RUN ["pytest", "--disable-warnings", "--maxfail=1", "--quiet"]

FROM python:3.12-slim
WORKDIR /app

# Copy pyproject.toml first (for dependency caching)
COPY pyproject.toml ./
COPY src/ ./src/
COPY README.md ./
COPY LICENSE ./

# Install dependencies
RUN pip install --no-cache-dir -e .

EXPOSE 8000

# compose.yaml overrides this with an auto-reloading dev server
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
