
FROM python:3.11-slim

RUN apt-get update && apt-get install -y nodejs npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/

WORKDIR /app

COPY app/requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app/package*.json /app/
RUN npm install

COPY app/ /app/

RUN npx tailwindcss -i ./static/css/input.css -o ./static/css/styles.css --minify

RUN groupadd --system appuser && useradd --system --create-home --gid appuser appuser
USER appuser

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--worker-class", "gthread", "--threads", "2", "--timeout", "60", "app:create_app()"]
