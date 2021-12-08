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
    logger_name = 'validator'
    logger = logging.getLogger(logger_name)
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
    def RDF_VALIDATOR_REPORT_TEMPLATE_LOCATION(self) -> str:
        if os.environ.get('RDF_VALIDATOR_TEMPLATE_LOCATION') \
                and Path(os.environ.get('RDF_VALIDATOR_TEMPLATE_LOCATION')).exists() \
                and any(Path(os.environ.get('RDF_VALIDATOR_TEMPLATE_LOCATION')).iterdir()):
            value = os.environ.get('RDF_VALIDATOR_TEMPLATE_LOCATION')
        else:
            value = str(Path(__file__).parents[1] / 'resources/templates/validator_report')
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
