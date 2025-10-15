# --- build/test stage ---
FROM python:3.12-slim AS test
WORKDIR /loan_analyzer
COPY pyproject.toml ./
COPY src/ ./src/
COPY tests/ ./tests/
RUN pip install --no-cache-dir .[test]
RUN ["pytest", "--verbose", "--disable-warnings", "--maxfail=1"]

# --- production stage ---
FROM python:3.12-slim
WORKDIR /loan_analyzer
COPY pyproject.toml ./
COPY src/ ./src/
RUN pip install --no-cache-dir .
ENTRYPOINT ["loan_analyzer_cli"]