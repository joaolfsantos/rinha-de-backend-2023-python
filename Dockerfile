FROM python:3.11-slim-buster

WORKDIR /app

COPY ./app /app/app

COPY pyproject.toml /app

RUN pip install poetry && \
    poetry export -f requirements.txt -o requirements.txt --without-hashes && \
    pip install -r requirements.txt

EXPOSE 9999

ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9999", "--workers", "14"]