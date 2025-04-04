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


def validate_file(data_file: FileStorage, schema_files: List[FileStorage]) -> tuple:
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

    response = requests.post(config.RDF_VALIDATOR_API_SERVICE + '/validate/shapes/file', files=files)
    return response.content, response.status_code


def validate_file_with_ap(data_file: FileStorage, application_profile: str) -> tuple:
    """
    Method to connect to the validator api to validate a file.
    :param data_file: The file to be validated
    :param application_profile: The application profile
    :return: state of the api response
    :rtype: file, int
    """
    files = {
        'data_file': (data_file.filename, data_file.stream, data_file.mimetype),
    }
    data = {
        'application_profile': application_profile
    }

    response = requests.post(config.RDF_VALIDATOR_API_SERVICE + '/validate/ap/file', files=files,
                             data=data)
    return response.content, response.status_code


def validate_sparql_endpoint(sparql_endpoint_url: str, schema_files: List[FileStorage],
                             graphs: list = None):
    """
    Method to connect to the validator api to validate a SPARQL endpoint.
    :param sparql_endpoint_url: The endpoint to validate
    :param schema_files: The content of the SHACL shape files defining the validation constraints
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

    response = requests.post(config.RDF_VALIDATOR_API_SERVICE + '/validate/shapes/url', data=data, files=files)
    return response.content, response.status_code


def validate_sparql_endpoint_with_ap(sparql_endpoint_url: str, application_profile: str,
                                     graphs: list = None):
    """
    Method to connect to the validator api to validate a SPARQL endpoint.
    :param sparql_endpoint_url: The endpoint to validate
    :param application_profile: The application profile
    :param graphs: An optional list of named graphs to restrict the scope of the validation
    :return:
    """
    data = {
        'sparql_endpoint_url': sparql_endpoint_url,
        'application_profile': application_profile
    }
    if graphs:
        data['graphs'] = graphs

    response = requests.post(config.RDF_VALIDATOR_API_SERVICE + '/validate/ap/url', json=data)
    return response.content, response.status_code


def get_application_profiles() -> tuple:
    """
    Method to get application profiles from api
    :return: application profiles
    :rtype list, int
    """
    response = requests.get(config.RDF_VALIDATOR_API_SERVICE + '/aps')
    return response.json(), response.status_code


def get_active_tasks() -> tuple:
    """
    Method to get celery active tasks from api
    :return: active celery tasks
    :rtype list, int
    """
    response = requests.get(config.RDF_VALIDATOR_API_SERVICE + '/tasks/active')
    return response.json(), response.status_code


def revoke_task(task_id: str) -> tuple:
    """
    Method to kill celery tasks from api
    :param task_id: celery task to kill
    :return: api response
    :rtype: dict, int
    """
    response = requests.delete(url=f'{config.RDF_VALIDATOR_API_SERVICE}/tasks/{task_id}')
    return response.json(), response.status_code


def get_validations() -> tuple:
    """
    Method to connect to the validator api to get validations.
    :return: the list of validations
    :rtype: list, int
    """
    response = requests.get(config.RDF_VALIDATOR_API_SERVICE + '/validations')
    return response.json(), response.status_code


def delete_validation(validation_id: str) -> tuple:
    """
    Method to connect to the validator api to delete validations.
    :param validation_id: The validation identifier.
    :rtype: dict, int
    """
    response = requests.delete(url=f'{config.RDF_VALIDATOR_API_SERVICE}/validations/{validation_id}')
    return response.json(), response.status_code


def get_report(validation_id: str, report_type: str) -> tuple:
    """
    Method to connect to the RDF diff api to get the validation diff report
    :param validation_id: The validation identifier.
    :param report_type: report variation
    :return: html report
    :rtype: file, int
    """
    response = requests.get(url=f'{config.RDF_VALIDATOR_API_SERVICE}/validations/{validation_id}',
                            params={
                                'report_type': report_type
                            })
    return response.content, response.status_code
