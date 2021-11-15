#!/usr/bin/python3

# api_wrapper.py
# Date:  24/09/2020
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com

"""
Service to consume validator API.
"""
from typing import List

import requests
from werkzeug.datastructures import FileStorage

from validator.config import config


def validate_file(data_file: FileStorage, schema_files: List[FileStorage], report_extension: str) -> tuple:
    """
    Method to connect to the validator api to validate a file.
    :param data_file: The file to be validated
    :param schema_files: The content of the SHACL shape files defining the validation constraints
    :param report_extension:
    :return: state of the api response
    :rtype: file, int
    """
    files = {
        'data_file': (data_file.filename, data_file.stream, data_file.mimetype),
    }
    for index, schema_file in enumerate(schema_files):
        files[f'schema_file{index}'] = (schema_file.filename, schema_file.stream, schema_file.mimetype)

    response = requests.post(config.RDF_VALIDATOR_API_SERVICE + '/validate-file', files=files,
                             params={'report_extension': report_extension})
    return response.content, response.status_code


def validate_sparql_endpoint(sparql_endpoint_url: str, schema_files: List[FileStorage], report_extension: str,
                             graphs: list = None):
    """
    Method to connect to the validator api to validate a SPARQL endpoint.
    :param sparql_endpoint_url: The endpoint to validate
    :param schema_files: The content of the SHACL shape files defining the validation constraints
    :param report_extension:
    :param graphs: An optional list of named graphs to restrict the scope of the validation
    :return:
    """
    data = {
        'sparql_endpoint_url': sparql_endpoint_url,
    }

    if graphs:
        data['graphs'] = graphs

    files = dict()
    for index, schema_file in enumerate(schema_files):
        files[f'schema_file{index}'] = (schema_file.filename, schema_file.stream, schema_file.mimetype)

    response = requests.post(config.RDF_VALIDATOR_API_SERVICE + '/validate-sparql-endpoint', data=data, files=files,
                             params={'report_extension': report_extension})
    return response.content, response.status_code
