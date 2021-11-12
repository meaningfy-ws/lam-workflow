#!/usr/bin/python3

# helpers.py
# Date:  01/10/2020
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com

"""
Helper methods

"""
import logging
from itertools import filterfalse

from rdflib.util import guess_format
from werkzeug.exceptions import BadRequest, UnsupportedMediaType, UnprocessableEntity

from validator.config import config

logger = logging.getLogger(config.RDF_VALIDATOR_LOGGER)

INPUT_MIME_TYPES = {
    'rdf': 'application/rdf+xml',
    'trix': 'application/xml',
    'nq': 'application/n-quads',
    'nt': 'application/n-triples',
    'jsonld': 'application/ld+json',
    'n3': 'text/n3',
    'ttl': 'text/turtle',
}

HTML_EXTENSION = 'html'
TTL_EXTENSION = 'ttl'
ZIP_EXTENSION = 'zip'

REPORT_EXTENSIONS = [TTL_EXTENSION, HTML_EXTENSION, ZIP_EXTENSION]
DEFAULT_REPORT_EXTENSION = REPORT_EXTENSIONS[0]


def _guess_file_type(file: str, accepted_types: dict = None):
    if accepted_types is None:
        accepted_types = INPUT_MIME_TYPES
    return guess_format(str(file), accepted_types)


def check_for_file_exceptions(schema_files, files_to_check, report_extension):
    """
    Helper method to check if validator configuration and files sent in request are compatible.
    :param schema_files: SHACL shape files sent from request
    :param files_to_check: files to check if file extension is supported
    :param report_extension: report extension to check if file extension is supported
    """
    if not config.RDF_VALIDATOR_ALLOWS_EXTRA_SHAPES and schema_files:
        exception_text = 'This configuration of the validator doesn\'t accept external SHACL shapes.'
        logger.exception(exception_text)
        raise BadRequest(exception_text)  # 400

    file_exceptions = list(filterfalse(lambda file: _guess_file_type(file.filename), files_to_check))
    if file_exceptions:
        exception_text = 'File type errors: ' + ', '.join([file.filename for file in file_exceptions]) + \
                         '. Acceptable types: ' + \
                         ', '.join([f'{key}({value})' for (key, value) in INPUT_MIME_TYPES.items()]) + '.'
        logger.exception(exception_text)
        raise UnsupportedMediaType(exception_text)  # 415

    if report_extension not in REPORT_EXTENSIONS:
        exception_text = 'Wrong report_extension format. Accepted formats: ' \
                         f'{", ".join([format for format in REPORT_EXTENSIONS])}'
        logger.exception(exception_text)
        raise UnprocessableEntity(exception_text)  # 422
