#!/usr/bin/python3

# handlers.py
# Date:  24/09/2020
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com

"""
OpenAPI method handlers.
"""
import logging
from pathlib import Path
from uuid import uuid4

from flask import send_file
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import NotAcceptable, NotFound

from validator.adapters.celery import async_validate_file, async_validate_url
from validator.config import config
from validator.entrypoints.api.helpers import check_for_file_exceptions, \
    check_report_extension
from validator.service_layer.ap_manager import ApplicationProfileManager
from validator.service_layer.db import save_data_for_validation
from validator.service_layer.report_handlers import get_report, get_available_validations, remove_all_reports, \
    remove_report
from validator.service_layer.tasks import flatten_active_tasks, retrieve_active_tasks, retrieve_task, kill_task

logger = logging.getLogger(config.RDF_VALIDATOR_LOGGER)


def validate_file_with_shacl(data_file: FileStorage,
                             schema_file0: FileStorage = None, schema_file1: FileStorage = None,
                             schema_file2: FileStorage = None,
                             schema_file3: FileStorage = None, schema_file4: FileStorage = None) -> tuple:
    """
    API method to handle file validation with custom shacl shapes files.
    :param data_file: The file to be validated
    :param schema_file0 - schema_file4: The content of the SHACL shape files defining the validation constraints
    :return: validation task id
    :rtype: dict, int
    """
    logger.debug('start validate file with shacl shapes endpoint')

    schema_files = list(filter(None, [schema_file0, schema_file1, schema_file2, schema_file3, schema_file4]))
    filenames = [file.filename for file in [data_file, *schema_files]]
    check_for_file_exceptions(schema_files, filenames)
    saved_location, save_file_to_validate, saved_shacl_shapes = save_data_for_validation(file_to_validate=data_file,
                                                                                         shacl_shapes=schema_files,
                                                                                         location=config.RDF_VALIDATOR_FILE_DB)
    task = async_validate_file.delay(str(uuid4()), save_file_to_validate, saved_shacl_shapes, saved_location)
    logger.debug('finish request to validate file with shacl shapes endpoint')
    return {'task_id': task.id}, 200


def validate_file_with_ap(body: dict, data_file: FileStorage) -> tuple:
    """
    API method to handle file validation.
    :param data_file: The file to be validated
    :param body: a dictionary with the json fields:
        :application_profile - application profile name
    :return: validation task id
    :rtype: dict, int
    """
    logger.debug('start validate file endpoint')
    application_profile = body.get('application_profile')
    apm = ApplicationProfileManager(application_profile=application_profile)
    try:
        schema_files = apm.list_ap_files_paths()
    except LookupError as e:
        logger.exception(str(e))
        raise NotAcceptable(str(e))  # 500

    filenames = [Path(shape_path).name for shape_path in schema_files]
    filenames.append(data_file.filename)
    check_for_file_exceptions(schema_files, filenames)
    saved_location, save_file_to_validate, _ = save_data_for_validation(file_to_validate=data_file,
                                                                        shacl_shapes=[],
                                                                        location=config.RDF_VALIDATOR_FILE_DB)
    task = async_validate_file.delay(str(uuid4()), save_file_to_validate, schema_files, saved_location,
                                     application_profile)
    logger.debug('finish request to validate file endpoint')
    return {'task_id': task.id}, 200


def validate_sparql_endpoint_with_shacl(body,
                                        schema_file0: FileStorage = None, schema_file1: FileStorage = None,
                                        schema_file2: FileStorage = None, schema_file3: FileStorage = None,
                                        schema_file4: FileStorage = None) -> tuple:
    """
    API method to handle SPARQL endpoint validation.
    :param body: a dictionary with the json fields:
        :sparql_endpoint_url - The endpoint to validate
        :graphs - An optional list of named graphs to restrict the scope of the validation
    :param schema_file0 - schema_file4: The content of the SHACL shape files defining the validation constraints
    :return: validation task id
    :rtype: dict, int
    """
    logger.debug('start validate sparql endpoint')

    schema_files = list(filter(None, [schema_file0, schema_file1, schema_file2, schema_file3, schema_file4]))
    filenames = [shape_path.filename for shape_path in schema_files]
    check_for_file_exceptions(schema_files, filenames)

    sparql_endpoint_url = body.get('sparql_endpoint_url')
    graphs = body.get('graphs')
    saved_location, _, saved_shacl_shapes = save_data_for_validation(file_to_validate=None,
                                                                     shacl_shapes=schema_files,
                                                                     location=config.RDF_VALIDATOR_FILE_DB)
    task = async_validate_url.delay(str(uuid4()), sparql_endpoint_url, graphs, saved_shacl_shapes, saved_location)

    logger.debug('finish request to validate sparql endpoint')
    return {'task_id': task.id}, 200


def validate_sparql_endpoint_with_ap(body) -> tuple:
    """
    API method to handle SPARQL endpoint validation.
    :param body: a dictionary with the json fields:
        :sparql_endpoint_url - The endpoint to validate
        :graphs - An optional list of named graphs to restrict the scope of the validation
        :application_profile - application profile name
    :return: validation task id
    :rtype: dict, int
    """
    logger.debug('start validate sparql endpoint')

    application_profile = body.get('application_profile')
    sparql_endpoint_url = body.get('sparql_endpoint_url')
    graphs = body.get('graphs')

    apm = ApplicationProfileManager(application_profile=application_profile)

    try:
        schema_files = apm.list_ap_files_paths()
    except LookupError as e:
        logger.exception(str(e))
        raise NotAcceptable(str(e))  # 500

    filenames = [Path(shape_path).name for shape_path in schema_files]
    check_for_file_exceptions(schema_files, filenames)
    saved_location, _, _ = save_data_for_validation(file_to_validate=None,
                                                    shacl_shapes=[],
                                                    location=config.RDF_VALIDATOR_FILE_DB)
    task = async_validate_url.delay(str(uuid4()), sparql_endpoint_url, graphs, schema_files, saved_location,
                                    application_profile)
    logger.debug('finish request to validate sparql endpoint')
    return {'task_id': task.id}, 200


def get_application_profiles_details() -> tuple:
    """
      Get all available application profiles and their available validation (shapes) files.
    :return: list[dict]
    :rtype: list, int
    """
    return [{"application_profile": ap,
             "shapes_files": ApplicationProfileManager(ap).list_ap_files()} for ap in
            ApplicationProfileManager().list_aps()], 200


def get_validations() -> tuple:
    """
    Get validation runs with their metadata.
    :return: list of run validations
    """
    validations = get_available_validations(config.RDF_VALIDATOR_REPORTS_DB)
    return validations, 200


def get_validation(uid: str, report_type: str) -> tuple:
    """
    Get validation report
    :param uid: unique identifier of the validation
    :param report_type: type of file to be returned. Can be `html`, `ttl`, or `zip`. Defaults to `ttl`
    :return: specified report
    """

    check_report_extension(report_type)
    try:
        location, filename = get_report(validation_uid=uid, extension=report_type,
                                        db_location=config.RDF_VALIDATOR_REPORTS_DB)
        return send_file(location, attachment_filename=filename)
    except FileNotFoundError:
        raise NotFound('Validation doesn\'t exist.')


def delete_validation(uid: str) -> tuple:
    """
    Delete specified validation reports
    :param uid: unique identifier of the validation
    """
    removed = remove_report(validation_uid=uid, db_location=config.RDF_VALIDATOR_REPORTS_DB)
    if removed:
        return {'message': f'Validation with {uid} successfully removed'}, 200
    else:
        raise NotFound(f'Validation with {uid} doesn\'t exist')


def delete_validations() -> tuple:
    """
    Delete all validation reports
    """
    remove_all_reports(db_location=config.RDF_VALIDATOR_REPORTS_DB)
    return {'message': f'Successfully removed all validations'}, 200


def get_active_tasks() -> tuple:
    """
    Get all active celery tasks
    :return: dict of celery workers and their active tasks
    """
    try:
        tasks = flatten_active_tasks(retrieve_active_tasks())
    except AttributeError:
        return [], 200
    return tasks, 200


def get_task_status(task_id: str) -> tuple:
    """
    Get specified task status data
    :param task_id: Id of task to get status for
    :return: dict
    """
    task = retrieve_task(task_id)
    if task:
        return {
                   "task_id": task.id,
                   "task_status": task.status,
                   "task_result": task.result
               }, 200
    raise NotFound('task not found')  # 404


def stop_running_task(task_id: str) -> tuple:
    """
    Revoke a task
    :param task_id: Id of task to revoke
    """
    try:
        tasks = flatten_active_tasks(retrieve_active_tasks())
        task = next(task for task in tasks if task["id"] == task_id)
        kill_task(task, config.RDF_VALIDATOR_REPORTS_DB)
    except:
        raise NotAcceptable('task already finished executing or does not exist')  # 406

    return {'message': f'task {task_id} set for revoking.'}, 200
