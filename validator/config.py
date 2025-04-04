#!/usr/bin/python3

# config.py
# Date: 09/10/2020
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com

"""
Project wide configuration file.
"""
import logging
import os
from distutils.util import strtobool
from pathlib import Path
from typing import Optional

API_TYPE = 'api'
UI_TYPE = 'ui'


class ValidatorConfig:
    logger_name = 'gunicorn.error'
    logger = logging
    type = None

    def set_as_api_server(self):
        self.type = API_TYPE
        self.check_if_custom_shacl_shapes_location_defined_but_no_files()
        self.check_if_valid_configuration()

    def set_as_ui_server(self):
        self.type = UI_TYPE

    def check_if_custom_shacl_shapes_location_defined_but_no_files(self):
        if os.environ.get('RDF_VALIDATOR_SHACL_SHAPES_LOCATION'):
            if not (Path(os.environ.get('RDF_VALIDATOR_SHACL_SHAPES_LOCATION')).exists()
                    and any(Path(os.environ.get('RDF_VALIDATOR_SHACL_SHAPES_LOCATION')).iterdir())):
                exception_text = 'RDF_VALIDATOR_SHACL_SHAPES_LOCATION was specified but no files found in the directory.'
                self.logger.fatal(exception_text)
                raise RuntimeError(exception_text)

    def check_if_valid_configuration(self):
        if not (os.environ.get('RDF_VALIDATOR_SHACL_SHAPES_LOCATION')
                and Path(os.environ.get('RDF_VALIDATOR_SHACL_SHAPES_LOCATION')).exists()
                and any(Path(os.environ.get('RDF_VALIDATOR_SHACL_SHAPES_LOCATION')).iterdir())) \
                and not self.RDF_VALIDATOR_ALLOWS_EXTRA_SHAPES:
            exception_text = 'The validator can\'t run in this configuration. ' \
                             'Set at least one  variables RDF_VALIDATOR_ALLOWS_EXTRA_SHAPES to True ' \
                             'or set the location for RDF_VALIDATOR_SHACL_SHAPES_LOCATION.'
            self.logger.fatal(exception_text)
            raise RuntimeError(exception_text)

    @property
    def RDF_VALIDATOR_LOGGER(self) -> str:
        value = self.logger_name
        self.logger.debug(value)
        return value

    @property
    def RDFUNIT_QUERY_DELAY_MS(self) -> int:
        value = int(os.environ.get('RDFUNIT_QUERY_DELAY_MS', 1))
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_DEBUG(self) -> bool:
        value = strtobool(os.environ.get('RDF_VALIDATOR_DEBUG', 'true'))
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_HTML_REPORT_TEMPLATE_LOCATION(self) -> str:
        if os.environ.get('RDF_VALIDATOR_HTML_REPORT_TEMPLATE_LOCATION') \
                and Path(os.environ.get('RDF_VALIDATOR_HTML_REPORT_TEMPLATE_LOCATION')).exists() \
                and any(Path(os.environ.get('RDF_VALIDATOR_HTML_REPORT_TEMPLATE_LOCATION')).iterdir()):
            value = os.environ.get('RDF_VALIDATOR_HTML_REPORT_TEMPLATE_LOCATION')
        else:
            value = str(Path(__file__).parents[1] / 'resources/templates/html')
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_JSON_REPORT_TEMPLATE_LOCATION(self) -> str:
        if os.environ.get('RDF_VALIDATOR_JSON_REPORT_TEMPLATE_LOCATION') \
                and Path(os.environ.get('RDF_VALIDATOR_JSON_REPORT_TEMPLATE_LOCATION')).exists() \
                and any(Path(os.environ.get('RDF_VALIDATOR_JSON_REPORT_TEMPLATE_LOCATION')).iterdir()):
            value = os.environ.get('RDF_VALIDATOR_JSON_REPORT_TEMPLATE_LOCATION')
        else:
            value = str(Path(__file__).parents[1] / 'resources/templates/json')
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_REPORT_TITLE(self) -> Optional[str]:
        value = os.environ.get('RDF_VALIDATOR_REPORT_TITLE', 'SHACL shape validation report').strip('"')
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_FILE_NAME_BASE(self) -> Optional[str]:
        value = os.environ.get('RDF_VALIDATOR_FILE_NAME_BASE', 'validation-report').strip('"')
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_UI_NAME(self) -> Optional[str]:
        value = os.environ.get('RDF_VALIDATOR_UI_NAME', 'RDF Validator').strip('"')
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_SHACL_SHAPES_LOCATION(self) -> Optional[str]:
        value = os.environ.get('RDF_VALIDATOR_SHACL_SHAPES_LOCATION')
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_ALLOWS_EXTRA_SHAPES(self) -> bool:
        value = strtobool(os.environ.get('RDF_VALIDATOR_ALLOWS_EXTRA_SHAPES', 'true'))
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_API_SERVICE(self) -> str:
        location = os.environ.get('RDF_VALIDATOR_API_LOCATION', 'http://fingerprinter-api')
        port = os.environ.get('RDF_VALIDATOR_API_PORT', 4010)
        value = f'{location}:{port}'
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_UI_SERVICE(self) -> str:
        location = os.environ.get('RDF_VALIDATOR_UI_LOCATION', 'http://fingerprinter-ui')
        port = os.environ.get('RDF_VALIDATOR_UI_PORT', 8010)
        value = f'{location}:{port}'
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_API_SECRET_KEY(self) -> str:
        value = os.environ.get('RDF_VALIDATOR_API_SECRET_KEY', 'secret key api')
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_UI_SECRET_KEY(self) -> str:
        value = os.environ.get('RDF_VALIDATOR_UI_SECRET_KEY', 'secret key api')
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_TIME_FORMAT(self) -> str:
        value = os.environ.get('RDF_VALIDATOR_TIME_FORMAT', '%d-%b-%YT%H:%M:%S')
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_TIMEZONE(self) -> str:
        value = os.environ.get('RDF_VALIDATOR_TIMEZONE', 'Europe/Paris')
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_REPORT_META_NAME(self) -> str:
        value = os.environ.get('RDF_VALIDATOR_REPORT_META_NAME', 'meta.json')
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_HTML_REPORT_NAME(self) -> str:
        value = os.environ.get('RDF_VALIDATOR_HTML_REPORT_NAME', 'report.html')
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_TTL_REPORT_NAME(self) -> str:
        value = os.environ.get('RDF_VALIDATOR_TTL_REPORT_NAME', 'report.ttl')
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_CUSTOM_HTML_REPORT_NAME(self) -> str:
        value = os.environ.get('RDF_VALIDATOR_CUSTOM_REPORT_NAME', 'custom.html')
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_CUSTOM_JSON_REPORT_NAME(self) -> str:
        value = os.environ.get('RDF_VALIDATOR_CUSTOM_JSON_REPORT_NAME', 'custom.json')
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_ZIP_REPORT_NAME(self) -> str:
        value = os.environ.get('RDF_VALIDATOR_ZIP_REPORT_NAME', 'report.zip')
        self.logger.debug(value)
        return value

    @property
    def SHOW_SWAGGER_UI(self) -> bool:
        value = strtobool(os.environ.get('SHOW_SWAGGER_UI', 'true'))
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_REDIS_SERVICE(self) -> str:
        location = os.environ.get('RDF_VALIDATOR_REDIS_LOCATION', 'redis://redis')
        port = os.environ.get('RDF_VALIDATOR_REDIS_PORT', 6379)
        value = f'{location}:{port}'
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_RDFUNIT_LOCATION(self) -> str:
        value = os.environ.get('RDF_VALIDATOR_RDFUNIT_LOCATION',
                               Path(__file__).parents[2] / 'rdfunit/rdfunit-validate.jar')
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_APS_LOCATION(self) -> str:
        value = os.environ.get('RDF_VALIDATOR_APS_LOCATION', Path(__file__).parents[1] / 'resources/shacl-shapes')
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_FILE_DB(self) -> str:
        value = os.environ.get('RDF_VALIDATOR_FILE_DB', str(Path(__file__).parents[1] / 'db'))
        self.logger.debug(value)
        return value

    @property
    def RDF_VALIDATOR_REPORTS_DB(self) -> str:
        value = os.environ.get('RDF_VALIDATOR_REPORTS_DB', str(Path(__file__).parents[1] / 'reports'))
        self.logger.debug(value)
        return value


config = ValidatorConfig()


class FlaskConfig:
    """
    Base Flask config
    """
    DEBUG = False
    TESTING = False


class ProductionConfig(FlaskConfig):
    """
    Production Flask config
    """


class DevelopmentConfig(FlaskConfig):
    """
    Development Flask config
    """
    DEBUG = True


class TestingConfig(FlaskConfig):
    """
    Testing Flask config
    """
    TESTING = True
    WTF_CSRF_ENABLED = False
