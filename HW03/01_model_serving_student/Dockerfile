FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt
COPY pyproject.toml .
COPY src/ ./src/
RUN pip install --prefix=/install --no-cache-dir -e .

FROM python:3.11-slim
COPY --from=builder /install /usr/local
COPY --from=builder /app /app
WORKDIR /app
EXPOSE 8000
CMD ["uvicorn", "airbnb_serving.app:app", "--host", "0.0.0.0", "--port", "8000"]