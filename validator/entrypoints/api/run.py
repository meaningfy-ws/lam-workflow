#!/usr/bin/python3

# run.py
# Date:  24/09/2020
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com

"""
Production API server through connexion definitions.
"""
import logging

from validator.config import ProductionConfig, DevelopmentConfig, config
from validator.entrypoints.api import app

if config.RDF_VALIDATOR_DEBUG:
    app.config.from_object(DevelopmentConfig())
else:
    app.config.from_object(ProductionConfig())

config.set_as_api_server()

if __name__ == '__main__':
    app.run()

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
