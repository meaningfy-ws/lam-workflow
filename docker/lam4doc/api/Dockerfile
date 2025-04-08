FROM python:3.11.11-slim

RUN apt-get update \
    && apt-get install -y texlive texlive-bibtex-extra texlive-latex-extra texlive-xetex texlive-lang-european lmodern --no-install-recommends \
    && apt --purge remove tex.\*-doc$

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
             --bind 0.0.0.0:${LAM_API_PORT:-4050} \
             -k uvicorn.workers.UvicornWorker \
             --timeout ${LAM_GUNICORN_TIMEOUT:-1200} \
             -w ${LAM_GUNICORN_API_WORKERS:-1} \
             lam4doc.entrypoints.api.run:app \
