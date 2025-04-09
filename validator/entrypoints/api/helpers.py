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
from os.path import splitext

from werkzeug.exceptions import BadRequest, UnsupportedMediaType, UnprocessableEntity

from validator.config import config
from validator.utils.constants import INPUT_MIME_TYPES, REPORT_EXTENSIONS

logger = logging.getLogger(config.RDF_VALIDATOR_LOGGER)


def _get_ext(fpath, lower=True):
    """
    Gets the file extension from a file(path); stripped of leading '.' and in
    lower case. Examples:

        >>> _get_ext("path/to/file.txt")
        'txt'
        >>> _get_ext("OTHER.PDF")
        'pdf'
        >>> _get_ext("noext")
        ''
        >>> _get_ext(".rdf")
        'rdf'
    """
    ext = splitext(fpath)[-1]
    if ext == '' and fpath.startswith("."):
        ext = fpath
    if lower:
        ext = ext.lower()
    if ext.startswith('.'):
        ext = ext[1:]
    return ext


def _guess_file_type(file: str, accepted_types: dict = None):
    """    Guess RDF serialization based on file suffix. Uses
    ``SUFFIX_FORMAT_MAP`` unless ``fmap`` is provided. Examples:

        >>> _guess_file_type('path/to/file.rdf')
        'xml'
        >>> _guess_file_type('path/to/file.owl')
        'xml'
        >>> _guess_file_type('path/to/file.ttl')
        'turtle'
        >>> _guess_file_type('path/to/file.json')
        'json-ld'
        >>> _guess_file_type('path/to/file.xhtml')
        'rdfa'
        >>> _guess_file_type('path/to/file.svg')
        'rdfa'
        >>> _guess_file_type('path/to/file.xhtml', {'xhtml': 'grddl'})
        'grddl'

    This also works with just the suffixes, with or without leading dot, and
    regardless of letter case::

        >>> _guess_file_type('.rdf')
        'xml'
        >>> _guess_file_type('rdf')
        'xml'
        >>> _guess_file_type('RDF')
        'xml'
    """
    if accepted_types is None:
        accepted_types = INPUT_MIME_TYPES
    return accepted_types.get(_get_ext(str(file))) or accepted_types.get(str(file).lower())


def check_for_file_exceptions(schema_files, files_to_check):
    """
    Helper method to check if validator configuration and files sent in request are compatible.
    :param schema_files: SHACL shape files sent from request
    :param files_to_check: files to check if file extension is supported
    """
    if not config.RDF_VALIDATOR_ALLOWS_EXTRA_SHAPES and schema_files:
        exception_text = 'This configuration of the validator doesn\'t accept external SHACL shapes.'
        logger.exception(exception_text)
        raise BadRequest(exception_text)  # 400

    file_exceptions = list(filterfalse(lambda file: _guess_file_type(file), files_to_check))
    if file_exceptions:
        exception_text = 'File type errors: ' + ', '.join([file for file in file_exceptions]) + \
                         '. Acceptable types: ' + \
                         ', '.join([f'{key}({value})' for (key, value) in INPUT_MIME_TYPES.items()]) + '.'
        logger.exception(exception_text)
        raise UnsupportedMediaType(exception_text)  # 415


def check_report_extension(report_type: str):
    """
    Check if required report type is accepted
    :param report_extension: report extension to check if file extension is supported
    """
    if report_type not in REPORT_EXTENSIONS:
        exception_text = 'Wrong report_extension format. Accepted formats: ' \
                         f'{", ".join([format for format in REPORT_EXTENSIONS])}'
        logger.exception(exception_text)
        raise UnprocessableEntity(exception_text)  # 422
