# syntax=docker/dockerfile:1.2

FROM python:3.11-slim

WORKDIR /app

RUN pip install poetry --root-user-action=ignore

COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

COPY main.py data_structures.py ./

ENTRYPOINT ["python", "main.py"]
