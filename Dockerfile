FROM python:3.12-alpine AS builder
WORKDIR /build


RUN pip install --no-cache-dir --no-compile --target /deps flask && \
    find /deps -type d -name "__pycache__" -prune -exec rm -rf {} + && \
    find /deps -type d -name "tests" -prune -exec rm -rf {} +

COPY app.py .
COPY templates/ ./templates/
COPY static/ ./static/
COPY todos.json .

FROM alpine:3.20

RUN apk add --no-cache python3

WORKDIR /app

RUN addgroup -S app && adduser -S app -G app

COPY --from=builder --chown=app:app /deps /app/deps
COPY --from=builder --chown=app:app /build /app

ENV PYTHONPATH=/app/deps \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN chmod 600 /app/todos.json \
    && chmod -R go-w /app

USER app

EXPOSE 5000
CMD ["python3", "app.py"]