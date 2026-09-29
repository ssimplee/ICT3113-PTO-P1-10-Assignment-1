FROM python:3.12.11-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY service/app ./app
RUN mkdir -p /data /logs

CMD ["python", "-m", "app"]
