#!/usr/bin/python3

"""
UI server through flask definitions.
"""
import logging

from lam4doc.config import config, ProductionConfig, DevelopmentConfig
from lam4doc.entrypoints.ui import app
from a2wsgi import WSGIMiddleware

if config.LAM_DEBUG:
    app.config.from_object(DevelopmentConfig())
else:
    app.config.from_object(ProductionConfig())

# Create an ASGI app from the Flask WSGI app
asgi_app = WSGIMiddleware(app)

if __name__ == '__main__':
    app.run()

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)