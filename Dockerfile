# Description: Dockerfile for the project

# Base image
FROM python:3.6 as base

# python envs
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN apt-get update \
    && apt-get install -y gettext libgettextpo-dev

RUN useradd --create-home --home-dir /app --shell /bin/bash app

WORKDIR /app

COPY src/requirements/base.txt \
    src/requirements/dev.txt \
    src/requirements/test.txt \
    src/requirements/prod.txt \
    /app/requirements/

RUN pip install -r requirements/base.txt

ADD src .

# Development image
FROM base as dev
RUN pip install -r requirements/dev.txt
RUN pip install -r requirements/test.txt
USER app
