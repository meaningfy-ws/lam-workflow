FROM python:3.11.11-slim

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements/common.txt ./requirements/common.txt

RUN pip install -r requirements/common.txt --no-cache-dir

COPY . /usr/src/app

CMD gunicorn --preload \
             --log-file=- \
             --access-logfile=- \
             --error-logfile=- \
             --log-level=debug \
             --capture-output \
             --bind 0.0.0.0:${LAM_UI_PORT:-8050} \
             -k uvicorn.workers.UvicornWorker \
             --timeout ${LAM_GUNICORN_TIMEOUT:-1200} \
             -w ${LAM_GUNICORN_API_WORKERS:-1} \
             lam4doc.entrypoints.ui.run:asgi_app \