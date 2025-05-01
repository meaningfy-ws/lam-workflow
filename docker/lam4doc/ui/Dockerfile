FROM python:3.11.11-slim

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements/common.txt ./requirements/common.txt

RUN pip install -r requirements/common.txt --no-cache-dir

COPY . /usr/src/app

CMD uvicorn lam4doc.entrypoints.ui.run:asgi_app --host 0.0.0.0 --port ${LAM_UI_PORT:-8050} --log-level debug