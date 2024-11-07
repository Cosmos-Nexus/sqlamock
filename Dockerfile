FROM python:3.12.6 AS builder

ENV PATH="/root/.local/bin:${PATH}"

RUN curl -sSL https://install.python-poetry.org | python3 - \
    && poetry self update \
    && poetry config virtualenvs.in-project true


COPY pyproject.toml poetry.lock /venv/

WORKDIR /venv/

RUN poetry install

FROM python:3.12.6

LABEL version="0.1.0"
LABEL author="Chris Lee"
LABEL email="chris@cosmosnexus.co"
LABEL description="sqlamock"

ENV PYTHONPATH=/sqlamock PATH=/venv/.venv/bin:/sqlamock/bin:${PATH}
COPY --from=builder /venv /venv

RUN apt update \
    && apt upgrade -y \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /sqlamock
COPY . /sqlamock


ENTRYPOINT [ "bash" ]
