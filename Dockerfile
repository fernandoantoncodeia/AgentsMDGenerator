FROM python:3.12-slim AS builder

WORKDIR /build
COPY pyproject.toml ./
COPY agentsmd ./agentsmd
RUN pip install --no-cache-dir build && python -m build --wheel .

FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /build/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

EXPOSE 3000

# The catalogue must be mounted at /app/prompt-catalogue
CMD ["agentsmd-server", "--transport", "sse", "--port", "3000", "--host", "0.0.0.0"]
