FROM node:20-slim AS builder

WORKDIR /build

COPY app/package*.json ./
COPY app/tailwind.config.js ./
COPY app/templates ./templates
COPY app/static/css/input.css ./static/css/input.css

RUN npm install
RUN npx tailwindcss -i ./static/css/input.css -o ./static/css/styles.css --minify

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

COPY --from=builder /build/static/css/styles.css ./static/css/styles.css

RUN groupadd --system appuser && useradd --system --create-home --gid appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--worker-class", "gthread", "--threads", "2", "--timeout", "60", "app:create_app()"]