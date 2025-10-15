# --- build/test stage ---
FROM python:3.12-slim AS test
WORKDIR /loan_analyzer
COPY pyproject.toml ./
COPY src/ ./src/
COPY tests/ ./tests/
RUN pip install --no-cache-dir .[test]
RUN ["pytest", "--disable-warnings", "--maxfail=1", "--quiet"]

# --- production stage ---
FROM python:3.12-slim
WORKDIR /loan_analyzer
COPY pyproject.toml ./
COPY src/ ./src/
RUN pip install --no-cache-dir .
ENTRYPOINT ["loan_analyzer_cli"]