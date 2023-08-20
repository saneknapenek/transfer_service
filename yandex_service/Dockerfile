FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

RUN curl -sSL https://install.python-poetry.org | python3 -

COPY ./ /yandex_service

WORKDIR /yandex_service

RUN ~/.local/share/pypoetry/venv/bin/poetry config virtualenvs.create false
RUN ~/.local/share/pypoetry/venv/bin/poetry update

EXPOSE 8001
