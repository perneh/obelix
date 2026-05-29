FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OBELIX_SHARED_CONFIGURATIONS_DIR=/app/configurations \
    OBELIX_LOCAL_CONFIGURATIONS_DIR=/app/data/configurations \
    OBELIX_SCENARIOS_DIR=/app/data/scenarios

COPY pyproject.toml README.md ./
COPY backend/ backend/
COPY frontend/ frontend/
COPY configurations/ configurations/
COPY docs/categories/ docs/categories/
COPY data/ data/

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "backend"]
