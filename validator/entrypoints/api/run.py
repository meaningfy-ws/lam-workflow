#!/usr/bin/python3

# run.py
# Date:  24/09/2020
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com

"""
Production API server through connexion definitions.
"""
import logging

import connexion
from flask import Flask

from validator.config import ProductionConfig, DevelopmentConfig, config

app = connexion.FlaskApp(__name__, specification_dir='openapi/')

flask_app: Flask = app.app

if config.RDF_VALIDATOR_DEBUG:
    flask_app.config.from_object(DevelopmentConfig())
else:
    flask_app.config.from_object(ProductionConfig())

config.set_as_api_server()

app.add_api('validator.yaml')

if __name__ == '__main__':
    app.run()

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    flask_app.logger.handlers = gunicorn_logger.handlers
    flask_app.logger.setLevel(gunicorn_logger.level)
