#!/usr/bin/python3

# handlers.py
# Date:  24/09/2020
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com

"""
OpenAPI method handlers.
"""
import logging
import tempfile
from pathlib import Path

from flask import send_file
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import InternalServerError

from validator.config import config
from validator.entrypoints.api.helpers import DEFAULT_REPORT_EXTENSION, check_for_file_exceptions
from validator.service_layer.handlers import build_report_from_file, build_report_from_sparql_endpoint

logger = logging.getLogger(config.RDF_VALIDATOR_LOGGER)


def validate_file(data_file: FileStorage,
                  schema_file0: FileStorage = None, schema_file1: FileStorage = None, schema_file2: FileStorage = None,
                  schema_file3: FileStorage = None, schema_file4: FileStorage = None,
                  report_extension: str = DEFAULT_REPORT_EXTENSION) -> tuple:
    """
    API method to handle file validation.
    :param data_file: The file to be validated
    :param schema_file0 - schema_file4: The content of the SHACL shape files defining the validation constraints
    :param report_extension: type of file to be returned. Can be `html`, `ttl`, or `zip`. Defaults to `ttl`
    :return: the validation report in the requested format
    :rtype: report file (html, ttl or zip format), int
    """
    logger.debug('start validate file endpoint')

    schema_files = list(filter(None, [schema_file0, schema_file1, schema_file2, schema_file3, schema_file4]))
    check_for_file_exceptions(schema_files, [data_file, *schema_files], report_extension)

    try:
        with tempfile.TemporaryDirectory() as temp_folder:
            local_data_file = Path(temp_folder) / str(data_file.filename)
            data_file.save(local_data_file)

            local_schema_files = list()
            for schema_file in schema_files:
                local_schema_file = Path(temp_folder) / str(schema_file.filename)
                schema_file.save(local_schema_file)
                local_schema_files.append(str(local_schema_file))

            report_path, report_filename = build_report_from_file(temp_folder,
                                                                  str(local_data_file),
                                                                  local_schema_files,
                                                                  report_extension, data_file.filename)
            logger.debug('finish validate file endpoint')
            return send_file(report_path, as_attachment=True, attachment_filename=report_filename)  # 200
    except Exception as e:
        logger.exception(str(e))
        raise InternalServerError(str(e))  # 500


def validate_sparql_endpoint(body,
                             schema_file0: FileStorage = None, schema_file1: FileStorage = None,
                             schema_file2: FileStorage = None, schema_file3: FileStorage = None,
                             schema_file4: FileStorage = None,
                             report_extension: str = DEFAULT_REPORT_EXTENSION) -> tuple:
    """
    API method to handle SPARQL endpoint validation.
    :param body: a dictionary with the json fields:
        :sparql_endpoint_url - The endpoint to validate
        :graphs - An optional list of named graphs to restrict the scope of the validation
    :param schema_file0 - schema_file4: The content of the SHACL shape files defining the validation constraints
    :param report_extension: type of file to be returned. Can be `html`, `ttl`, or `zip`. Defaults to `ttl`
    :return: the validation ttl file
    :rtype: ttl file, int
    """
    logger.debug('start validate sparql endpoint')

    schema_files = list(filter(None, [schema_file0, schema_file1, schema_file2, schema_file3, schema_file4]))
    check_for_file_exceptions(schema_files, schema_files, report_extension)

    sparql_endpoint_url = body.get('sparql_endpoint_url')
    graphs = body.get('graphs')

    try:
        with tempfile.TemporaryDirectory() as temp_folder:
            local_schema_files = list()
            for schema_file in schema_files:
                local_schema_file = Path(temp_folder) / str(schema_file.filename)
                schema_file.save(local_schema_file)
                local_schema_files.append(str(local_schema_file))

            report_path, report_filename = build_report_from_sparql_endpoint(temp_folder,
                                                                             sparql_endpoint_url,
                                                                             graphs,
                                                                             local_schema_files,
                                                                             report_extension,
                                                                             'filename')
            logger.debug('finish validate sparql endpoint')
            return send_file(report_path, as_attachment=True, attachment_filename=report_filename)  # 200
    except Exception as e:
        logger.exception(str(e))
        raise InternalServerError(str(e))  # 500
