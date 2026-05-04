FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements-dev.txt requirements.txt ./
RUN pip install --no-cache-dir --prefix=/install -r requirements-dev.txt

FROM python:3.11-slim AS runtime
WORKDIR /app
RUN adduser --disabled-password --gecos '' appuser
COPY --from=builder /install /usr/local
COPY . .
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
