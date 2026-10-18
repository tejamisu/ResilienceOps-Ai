# ResilienceOps AI on Cloud Run: the agents' API and the app in one container.
# Build the app first (./prepare_web.sh copies test-run/resilienceops.html to web/index.html).
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8080
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD exec uvicorn api:app --host 0.0.0.0 --port ${PORT}
